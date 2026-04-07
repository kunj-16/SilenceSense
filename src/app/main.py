from fastapi import FastAPI, UploadFile, Form
import json

from src.app.text.chat_parser import parse_chat
from src.app.analysis.embeddings import EmbeddingModel
from src.app.analysis.metrics import compute_metrics

from src.app.analysis.ideas import (
    detect_ideas,
    detect_idea_reuse,
    detect_ignored_but_reused
)

from src.app.analysis.dominance import analyze_dominance_vs_value
from src.app.analysis.dominance_rules import generate_dominance_insights

from src.app.analysis.timing import analyze_silence_and_timing
from src.app.analysis.timing_rules import generate_timing_insights

from src.app.reports.report_generator import generate_participant_report
from src.app.reports.pdf_generator import generate_pdf_report

from src.app.mailer.email_sender import send_email_with_attachment


app = FastAPI()
embedder = EmbeddingModel()


@app.post("/analyze/chat")
async def analyze_chat(
    file: UploadFile,
    email_map: str = Form(None)  # Optional JSON mapping of speaker → email
):
    # ------------------------
    # Save Uploaded File
    # ------------------------
    path = f"data/uploads/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    # ------------------------
    # Analysis Pipeline
    # ------------------------
    events = parse_chat(path)
    texts = [e.text for e in events]

    embeddings = embedder.encode(texts)
    idea_flags = detect_ideas(events, embeddings)
    metrics = compute_metrics(events)

    reuse_map = detect_idea_reuse(events, embeddings, idea_flags)

    ignored_reused_map = detect_ignored_but_reused(
        events,
        embeddings,
        idea_flags,
        reuse_map
    )

    dominance_stats = analyze_dominance_vs_value(
        events,
        idea_flags,
        reuse_map
    )

    dominance_insights = generate_dominance_insights(
        dominance_stats
    )

    timing_stats = analyze_silence_and_timing(
        events,
        idea_flags,
        reuse_map
    )

    timing_insights = generate_timing_insights(
        timing_stats
    )

    # ------------------------
    # Build Raw Response
    # ------------------------
    response = {}

    for speaker, m in metrics.items():

        speaker_idea_indices = [
            i for i, e in enumerate(events)
            if e.speaker == speaker and idea_flags[i]
        ]

        ideas_data = [
            {
                "idea_text": events[idx].text,
                "introduced_at": round(events[idx].start_time, 2),
                "reused_by": reuse_map.get(idx, [])
            }
            for idx in speaker_idea_indices
        ]

        response[speaker] = {
            "metrics": {
                "turns": m["turns"],
                "total_time": round(m["time"], 2)
            },
            "ideas_introduced": ideas_data,
            "ignored_but_reused": [
                ignored_reused_map[i]
                for i in speaker_idea_indices
                if i in ignored_reused_map
            ],
            "dominance_value_metrics": dominance_stats.get(speaker, {}),
            "dominance_value_insights": dominance_insights.get(speaker, []),
            "silence_timing_metrics": timing_stats.get(speaker, {}),
            "silence_timing_insights": timing_insights.get(speaker, [])
        }

    # ------------------------
    # Generate Participant Reports
    # ------------------------
    reports = {}

    for speaker, speaker_data in response.items():
        reports[speaker] = generate_participant_report(
            speaker,
            speaker_data
        )

    # ------------------------
    # Generate PDFs
    # ------------------------
    pdf_paths = {}

    for speaker, report_data in reports.items():
        pdf_path = generate_pdf_report(report_data)
        pdf_paths[speaker] = pdf_path

    # ------------------------
    # Optional Email Sending
    # ------------------------
    email_status = {}

    if email_map:
        try:
            email_dict = json.loads(email_map)

            for speaker, recipient_email in email_dict.items():
                if speaker in pdf_paths:
                    send_email_with_attachment(
                        recipient_email=recipient_email,
                        subject="Your SilenceSense Participation Report",
                        body=f"""Hello {speaker},

Attached is your SilenceSense post-interaction analysis report.

This report is confidential and intended only for you.

Regards,
SilenceSense System
""",
                        attachment_path=pdf_paths[speaker]
                    )
                    email_status[speaker] = "Email Sent"

        except Exception as e:
            email_status["error"] = str(e)

    # ------------------------
    # Final Response
    # ------------------------
    return {
        "raw_analysis": response,
        "participant_reports": reports,
        "pdf_reports": pdf_paths,
        "email_status": email_status
    }