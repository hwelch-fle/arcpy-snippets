from builtins import print as _print
from typing import Literal
from _typeshed import SupportsWrite

from arcpy import AddMessage
from arcpy.mp import ArcGISProject
from arcpy._mp import Map, Layer
from arcpy.cim import CIMFeatureLayer, CIMFeatureTable, CIMFieldDescription

# Define a custom print function that also writes to the ArcGIS Pro messages
def print(
    *values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file: SupportsWrite[str] | None = None,
    flush: Literal[False] = False,
) -> None:
    _print(*values, sep=sep, end=end, file=file, flush=flush)
    AddMessage(sep.join(map(str, values)) + end if end != '\n' else '')

def update_field_visibility(
    aprx_path: str, 
    map_name: str, 
    *, 
    visible_fields: tuple[str]= (), 
    use_alias: bool = False,
    verbose: bool = False):
    
    # Open the project and get the layers
    aprx = ArcGISProject(aprx_path)
    map_doc: Map = aprx.listMaps(map_name)[0]
    layers: list[Layer] = [layer for layer in map_doc.listLayers() if layer.isFeatureLayer]
    
    # Update the field visibility for each layer
    for layer in layers:
        # Get CIM objects
        cim_lyr: CIMFeatureLayer = layer.getDefinition('V2')
        cim_feature_table: CIMFeatureTable = cim_lyr.featureTable
        cim_field_descriptions: list[CIMFieldDescription] = cim_feature_table.fieldDescriptions
        
        # Update field visibility
        for fd in cim_field_descriptions:
            name = (use_alias and fd.alias) or fd.fieldName
            
            if name not in visible_fields and fd.visible:
                fd.visible = False
                print(f"Field {name} for {layer.name} is now hidden")
            
            elif name in visible_fields and not fd.visible:
                fd.visible = True
                print(f"Field {name} for {layer.name} is now visible")
        
        # Set the definition
        layer.setDefinition(cim_lyr)
    
    # Save the project
    aprx.save()
    
if __name__ == "__main__":
    aprx = r"Path\To\APRX"
    map_name = "Map"
    visible_fields = ("Field1", "Field2", "Field3")
    
    update_field_visibility(aprx, map_name, visible_fields=visible_fields)