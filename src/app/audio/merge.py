from src.app.schemas.interaction import InteractionEvent

def assign_speaker(segment, diarization):
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if turn.start <= segment["start"] <= turn.end:
            return speaker
    return "unknown"

def merge_segments(segments, diarization):
    events = []
    for seg in segments:
        events.append(
            InteractionEvent(
                speaker=assign_speaker(seg, diarization),
                start_time=seg["start"],
                end_time=seg["end"],
                text=seg["text"]
            )
        )
    return events
