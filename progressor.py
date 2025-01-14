from dataclasses import dataclass
from arcpy import SetProgressor, SetProgressorLabel, SetProgressorPosition, ResetProgressor
from typing import Literal

@dataclass(slots=True)
class Progressor:
    label: str
    style: Literal['default', 'step'] = 'step'
    range: range
    
    def __post_init__(self):
        self._position: int = 0

    def __enter__(self):
        SetProgressor(self.style, self.label, self.range.start, self.range.stop, self.range.step)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        ResetProgressor()

    def __iter__(self):
        return self

    def __call__(self, label: str):
        SetProgressorLabel(label)
    
    def __next__(self):
        SetProgressorPosition()
        self._position += 1
        if self._position > self.range.stop: # inclusive range
            raise StopIteration
        yield self._position