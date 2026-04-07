def generate_timing_insights(timing_stats):
    """
    Converts silence and timing stats into human-readable insights.
    """

    insights = {}

    for speaker, s in timing_stats.items():
        speaker_insights = []

        # Ignore silence insights for very short interactions
        if timing_stats[speaker]["turns"] == 1 and len(timing_stats) <= 4:
            continue

        if s["silence_ratio"] >= 0.6 and s["turns"] <= 2:
            speaker_insights.append(
                "Participated briefly with long periods of inactivity"
            )


        if s["entry_phase"] == "late":
            speaker_insights.append(
                "Joined the discussion later than most participants"
            )

        if s["late_idea"] and s["late_impact"]:
            speaker_insights.append(
                "Introduced a late idea that influenced subsequent discussion"
            )

        insights[speaker] = speaker_insights

    return insights
