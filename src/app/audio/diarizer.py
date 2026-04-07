from pyannote.audio import Pipeline

class SpeakerDiarizer:
    def __init__(self):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization"
        )

    def diarize(self, audio_path):
        return self.pipeline(audio_path)
