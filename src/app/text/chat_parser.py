import re
from datetime import datetime
from src.app.schemas.interaction import InteractionEvent

pattern = r"(.*?) - (.*?): (.*)"

def parse_chat(file_path):
    events = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(pattern, line)
            if not match:
                continue

            time_str, speaker, text = match.groups()
            timestamp = datetime.strptime(
                time_str, "%d/%m/%y, %I:%M %p"
            ).timestamp()

            events.append(
                InteractionEvent(
                    speaker=speaker,
                    start_time=timestamp,
                    end_time=timestamp + max(len(text) * 0.04, 1),
                    text=text
                )
            )
    return events
