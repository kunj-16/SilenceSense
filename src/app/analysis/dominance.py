from collections import defaultdict


def analyze_dominance_vs_value(
    events,
    idea_flags,
    reuse_map
):
    """
    Computes participant-level dominance and value signals.
    """

    stats = defaultdict(lambda: {
        "turns": 0,
        "idea_count": 0,
        "reuse_count": 0,
        "non_idea_turns": 0
    })

    # Pass 1: basic counts
    for idx, event in enumerate(events):
        speaker = event.speaker
        stats[speaker]["turns"] += 1

        if idea_flags[idx]:
            stats[speaker]["idea_count"] += 1
            stats[speaker]["reuse_count"] += len(reuse_map.get(idx, []))
        else:
            stats[speaker]["non_idea_turns"] += 1

    # Pass 2: derive ratios
    for speaker, s in stats.items():
        s["semantic_contribution_ratio"] = round(
            s["idea_count"] / s["turns"], 3
        )

    return stats
