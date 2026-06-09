from abc import abstractmethod, ABC
from typing import Callable


class Renderer(ABC):
    """An object that renders information"""

    @abstractmethod
    def render(self, message: str) -> None:
        pass

    @abstractmethod
    def ask_decision(self, message: str) -> str:
        pass

    @abstractmethod
    def ask_with_validation(
        self,
        prompt: str,
        error_prefix: str,
        preprocess: Callable[[str], str],
        validator: Callable[[str], bool],
    ) -> str:
        pass


class ConsoleRenderer(Renderer):
    def render(self, message: str) -> None:
        print(message)

    def ask_decision(self, message: str) -> str:
        return input(message)

    def ask_with_validation(
        self,
        prompt: str,
        error_prefix: str,
        validator: Callable[[str], bool],
        preprocess: Callable[[str], str] = lambda x: x.strip(),
    ) -> str:
        raw_input = self.ask_decision(message=prompt)
        processed_input = preprocess(raw_input)
        while not validator(processed_input):
            error_prompt = f"{error_prefix} {prompt}"
            raw_input = self.ask_decision(message=error_prompt)
            processed_input = preprocess(raw_input)
        return processed_input
