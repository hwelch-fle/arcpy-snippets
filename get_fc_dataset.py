from __future__ import annotations
from pathlib import Path
from arcpy import Describe, ListDatasets, EnvManager
from functools import lru_cache

# For Describe type hinting
try:
    from arcpy.typing.describe import FeatureClass
except ImportError: # will fail at runtime do to malformed package
    pass

def get_fc_dataset(fc: Path) -> str:
    fc = Path(fc)
    fc_desc: FeatureClass = Describe(str(fc))
    fc_dataset = fc.parent
    wsp_path = Path(fc_desc.workspace.catalogPath)
    if fc_dataset != wsp_path:
        return str(fc_dataset.relative_to(wsp_path))

def get_fc_dataset_list(fc: str) -> str:
    fc_desc: FeatureClass = Describe(fc)
    with EnvManager(workspace=fc_desc.workspace.catalogPath):
        for ds in ListDatasets():
            if ds in fc:
                return ds
    
    
        
path = r"C:\Users\asimov\Desktop\Westchase 3.1\LLD_Design.gdb\Design\Span"