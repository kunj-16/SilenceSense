def generate_dominance_insights(stats):
    """
    Converts dominance/value metrics into explainable insights.
    """

    insights = {}

    for speaker, s in stats.items():
        speaker_insights = []

        if s["turns"] >= 5 and s["semantic_contribution_ratio"] < 0.3:
            speaker_insights.append(
                "High participation with limited introduction of new ideas"
            )

        if s["idea_count"] <= 1 and s["non_idea_turns"] >= 3:
            speaker_insights.append(
                "Primarily contributed through agreement or reinforcement"
            )

        if s["turns"] <= 3 and s["reuse_count"] >= 1:
            speaker_insights.append(
                "Selective participation with high impact on discussion"
            )

        if s["idea_count"] >= 2 and s["reuse_count"] >= 2:
            speaker_insights.append(
                "Introduced multiple ideas that influenced later discussion"
            )

        insights[speaker] = speaker_insights

    return insights
