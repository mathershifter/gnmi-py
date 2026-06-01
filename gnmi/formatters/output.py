from typing import Protocol, Generic, TypeVar

from gnmi.models.model import BaseModel

T = TypeVar("T", bound=BaseModel, contravariant=True)


class Sinker(Protocol, Generic[T]):
    def send(self, data: T) -> None: ...


# def render(data: BaseModel, sinker: Sinker) -> None:
#     sinker.send(data)
