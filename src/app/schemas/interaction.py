from dataclasses import dataclass

@dataclass
class InteractionEvent:
    speaker: str
    start_time: float
    end_time: float
    text: str
