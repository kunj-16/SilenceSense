import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch


def generate_pdf_report(report_data, output_dir="data/reports"):
    """
    Generates a PDF report for a participant.
    """

    os.makedirs(output_dir, exist_ok=True)

    participant = report_data["participant"]
    filename = f"{participant}_report.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(filepath)
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    heading_style = styles["Heading1"]

    # Title
    elements.append(Paragraph(
        f"SilenceSense Report - Participant {participant}",
        heading_style
    ))
    elements.append(Spacer(1, 0.5 * inch))

    # Overview
    overview = report_data["overview"]
    elements.append(Paragraph(
        f"Participation Turns: {overview['participation_turns']}",
        normal_style
    ))
    elements.append(Paragraph(
        f"Total Active Time: {overview['total_active_time']} seconds",
        normal_style
    ))
    elements.append(Spacer(1, 0.5 * inch))

    # Idea Contribution
    ideas = report_data["idea_contribution"]
    elements.append(Paragraph(
        f"Ideas Introduced: {ideas['ideas_introduced']}",
        normal_style
    ))
    elements.append(Paragraph(
        f"Ideas Influencing Others: {ideas['ideas_influencing_others']}",
        normal_style
    ))
    elements.append(Spacer(1, 0.5 * inch))

    # Strengths
    elements.append(Paragraph("Strengths:", styles["Heading2"]))
    for s in report_data["strengths"]:
        elements.append(Paragraph(f"- {s}", normal_style))

    elements.append(Spacer(1, 0.5 * inch))

    # Growth Areas
    elements.append(Paragraph("Areas for Growth:", styles["Heading2"]))
    for g in report_data["growth_areas"]:
        elements.append(Paragraph(f"- {g}", normal_style))

    doc.build(elements)

    return filepath
