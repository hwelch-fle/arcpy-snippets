from typing import (
    Any,
    Generator,
    Iterable,
    TypeVar,
    Generic,
)

def flatten(sequence: Iterable[Any]) -> Generator[Any, None, None]:
    for item in sequence:
        if not isinstance(item, Iterable):
            yield item
        else:
            yield from flatten(item)

T = TypeVar('T')            
class Flattener(Generic[T]):
    
    def flatten(self, sequence: Iterable[T]) -> Generator[T, None, None]:
        for item in sequence:
            # Iterate everything but strings (they are infinite)
            if isinstance(item, Iterable) and not isinstance(item, str):
                yield from self.flatten(item)
            
            # No Concrete Generic Filter
            elif not hasattr(self, '__orig_class__'):
                yield item
            
            # Has Concrete Generic Filter 
            elif isinstance(item, self.__orig_class__.__args__[0]):
                yield item
                
    def __mul__(self, other) -> list[T]:
        return list(self.flatten(other))
            