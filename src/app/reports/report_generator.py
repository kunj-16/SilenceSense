def generate_participant_report(
    speaker,
    data
):
    """
    Converts analysis output into a human-readable participant report.
    """

    report = {
        "participant": speaker,
        "overview": {},
        "idea_contribution": {},
        "interaction_style": [],
        "strengths": [],
        "growth_areas": []
    }

    # -----------------------------
    # Overview
    # -----------------------------
    metrics = data["metrics"]
    report["overview"] = {
        "participation_turns": metrics["turns"],
        "total_active_time": metrics["total_time"]
    }

    # -----------------------------
    # Idea Contribution
    # -----------------------------
    ideas = data["ideas_introduced"]
    report["idea_contribution"]["ideas_introduced"] = len(ideas)

    reused_ideas = [
        idea for idea in ideas
        if idea["reused_by"]
    ]
    report["idea_contribution"]["ideas_influencing_others"] = len(reused_ideas)

    # -----------------------------
    # Strengths
    # -----------------------------
    if reused_ideas:
        report["strengths"].append(
            "Introduced ideas that influenced the direction of the discussion"
        )

    for insight in data["dominance_value_insights"]:
        if "high impact" in insight.lower():
            report["strengths"].append(
                "Demonstrated high impact despite limited participation"
            )

    for insight in data["silence_timing_insights"]:
        if "late idea" in insight.lower():
            report["strengths"].append(
                "Made impactful contributions even when joining later"
            )

    # -----------------------------
    # Interaction Style
    # -----------------------------
    report["interaction_style"].extend(
        data["dominance_value_insights"]
    )
    report["interaction_style"].extend(
        data["silence_timing_insights"]
    )

    # -----------------------------
    # Growth Areas
    # -----------------------------
    if (
        data["dominance_value_metrics"]["semantic_contribution_ratio"] < 0.3
        and metrics["turns"] > 3
    ):
        report["growth_areas"].append(
            "Could increase impact by introducing more original ideas"
        )

    if not ideas and metrics["turns"] <= 2:
        report["growth_areas"].append(
            "May benefit from sharing ideas more actively in group discussions"
        )

    return report
