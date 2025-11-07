from enum import Enum
from log_diagnosis.models.manager import ModelTemplate
from transformers import pipeline

class ZeroShotModels(Enum):
    BART = 'facebook/bart-large-mnli'
    CROSSENCODER = 'cross-encoder/nli-MiniLM2-L6-H768'

class ModelZeroShotClassifer(ModelTemplate):
    def __init__(self, type=ZeroShotModels.CROSSENCODER):
        super().__init__()
        self.type = type

    def init_model(self):
        self.pipe = pipeline(task='zero-shot-classification', model=self.type.value)

    def classify_golden_signal(self, input: list[str], batch_size: int=32):
        candidate_labels = ["information", "error", "availability", "latency", "saturation", "traffic"]
        results = self.pipe(input, candidate_labels, batch_size=batch_size)
        if isinstance(results, dict):
            results = [results]
        return results
    
    def classify_fault_category(self, input: list[str], batch_size: int=32):
        candidate_labels = ["io", "authentication", "network", "application", "device"]
        results = self.pipe(input, candidate_labels, batch_size=batch_size)
        if isinstance(results, dict):
            results = [results]
        return results
