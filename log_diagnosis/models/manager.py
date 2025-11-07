from abc import ABC, abstractmethod

class ModelTemplate(ABC):
    @abstractmethod
    def init_model(self):
        pass

    @abstractmethod
    def classify_golden_signal(self, input: list[str], batch_size: int=32):
        pass

    @abstractmethod
    def classify_fault_category(self, input: list[str], batch_size: int=32):
        pass
