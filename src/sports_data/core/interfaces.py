import abc
from typing import Any

class BaseExtractor(abc.ABC):
    @abc.abstractmethod
    def extract(self, **kwargs: Any) -> Any:
        pass

class BaseTransformer(abc.ABC):
    @abc.abstractmethod
    def transform(self, data: Any) -> Any:
        pass

class BaseLoader(abc.ABC):
    @abc.abstractmethod
    def load(self, data: Any) -> None:
        pass
