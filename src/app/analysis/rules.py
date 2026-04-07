def generate_insight(metrics, idea_count):
    insights = []

    if metrics["turns"] > 15 and idea_count < 3:
        insights.append("High participation with limited new ideas")

    if metrics["turns"] < 5 and idea_count >= 3:
        insights.append("Low frequency but high semantic contribution")

    return insights
