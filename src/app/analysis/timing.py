from collections import defaultdict


def analyze_silence_and_timing(events, idea_flags, reuse_map):
    """
    Analyzes silence duration and timing of contributions.
    """

    stats = defaultdict(lambda: {
        "first_turn_time": None,
        "last_turn_time": None,
        "turns": 0,
        "late_idea": False,
        "late_impact": False
    })

    discussion_start = events[0].start_time
    discussion_end = events[-1].end_time
    total_duration = discussion_end - discussion_start

    late_threshold = discussion_start + 0.7 * total_duration

    # Pass 1: collect timing stats
    for idx, event in enumerate(events):
        speaker = event.speaker
        stats[speaker]["turns"] += 1

        if stats[speaker]["first_turn_time"] is None:
            stats[speaker]["first_turn_time"] = event.start_time

        stats[speaker]["last_turn_time"] = event.end_time

        # Late idea detection
        if idea_flags[idx] and event.start_time >= late_threshold:
            stats[speaker]["late_idea"] = True

            if reuse_map.get(idx):
                stats[speaker]["late_impact"] = True

    # Pass 2: derive silence ratio
    for speaker, s in stats.items():
        active_time = s["last_turn_time"] - s["first_turn_time"]
        silence_time = total_duration - active_time

        s["silence_ratio"] = round(
            silence_time / total_duration, 3
        )

        # Entry phase classification
        entry_offset = s["first_turn_time"] - discussion_start

        if entry_offset <= 0.3 * total_duration:
            s["entry_phase"] = "early"
        elif entry_offset <= 0.6 * total_duration:
            s["entry_phase"] = "mid"
        else:
            s["entry_phase"] = "late"

    return stats
