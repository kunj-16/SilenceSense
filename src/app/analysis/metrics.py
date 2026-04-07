from collections import defaultdict

def compute_metrics(events):
    stats = defaultdict(lambda: {
        "time": 0,
        "turns": 0
    })

    for e in events:
        stats[e.speaker]["time"] += e.end_time - e.start_time
        stats[e.speaker]["turns"] += 1

    return stats
