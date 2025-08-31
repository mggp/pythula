from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModel, pipeline
from choices import id2label, best_device, DomainEnum
from typing import Callable
from abc import abstractmethod

class CodeClassifier:
    def __init__(self, device=None):
        self._model: AutoModel = None
        self._tokenizer: AutoTokenizer = None
        self.id2label: Callable[[int, str]] = id2label
        self.device: str = device if device else best_device

    @abstractmethod
    def classify(self, code_snippet: str) -> DomainEnum:
        pass
    

class LocalHFClassifier(CodeClassifier):
    def __init__(self, model_path: str, device: str = None):
        super().__init__(device=device)

        self._classifier = pipeline("text-classification", model=model_path, tokenizer=model_path, device=device)

    def classify(self, code_snippet) -> DomainEnum:
        return self._classifier(code_snippet)[0]["label"]
