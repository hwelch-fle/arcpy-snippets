from pathlib import Path

from arcpy.mp import LayerFile, ArcGISProject
from arcpy._mp import Map, Layer # Hidden mp types

from arcpy.cim import CIMDefinition # All CIM types support the useSourceMetadata property

def get_map(project: ArcGISProject, map_name: str) -> Map:
    return project.listMaps(map_name)[0]

def set_metadata_readonly(project: ArcGISProject, layerfiles: list[str], output_map: str | None=None):
    """Adds layerfiles to a map then sets the useSourceMetadata property to True.
    
    Parameters:
        project (ArcGISProject): The project to add the layers to.
        layerfiles (list[str]): The list of layerfiles to add to the map.
        output_map (Optional[str]): The name of the map to add the layers to. (default is first map in project)
    """
    for layer_path in layerfiles:
        # Set Up LayerFile object
        lyrpath =  Path(layer_path)
        lyr = LayerFile(str(lyrpath))
        
        # Add Layer to top of map
        target_map = get_map(project, output_map)
        target_map.addLayer(lyr, add_position="TOP")
        
        # Get the new layer
        new_layer: Layer = target_map.listLayers()[0]
        
        # Get CIM definition for new layer
        new_layer_cim: CIMDefinition = new_layer.getDefinition("V3")
        
        # Set CIM useSourceMetadata to True
        new_layer_cim.useSourceMetadata = True
        
        # Update CIM definition
        new_layer.setDefinition(new_layer_cim)
            
def main():
    ## Implement your script here
    return

if __name__ == "__main__":
    main()