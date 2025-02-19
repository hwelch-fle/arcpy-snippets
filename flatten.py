from typing import (
    Any,
    Generator,
    Iterable,
)

def flatten(sequence: Iterable[Any]) -> Generator[Any, None, None]:
    for item in sequence:
        if not isinstance(item, Iterable):
            yield item
        else:
            yield from flatten(item)