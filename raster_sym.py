import arcpy
from arcpy._mp import ArcGISProject, Layer, ColorRamp, Symbology
from arcpy._symbology import RasterClassifyColorizer

from arcpy.cim import (
    CIMRasterLayer, 
    CIMRasterClassifyColorizer, 
    CIMRasterClassBreak, 
    ClassificationMethod, 
)

def build_breaks(min_break: int, max_break: int, total_breaks: int, 
                 units: str = '%', 
                 zero_break: str = 'No Change') -> list[tuple[int, str]]:
    """Build breaks and labels for the colorizer
    
    Args:
        min_break (int): The minimum break value (> -100)
        max_break (int): The maximum break value (< 100)
        total_breaks (int): The total number of breaks
        skip_zero (bool, optional): Skip the zero break if it is in the step. Defaults to True.
    """
    # Raise some errors if the input is invalid
    if min_break > max_break:
        raise ValueError("min_break must be less than max_break")
    
    if min_break <= -100:
        raise ValueError("min_break must be greater than -100")

    if max_break >= 100:
        raise ValueError("max_break must be less than 100")
    
    # Calculate the step (total_breaks has the 2 extremes removed)
    step = int((max_break - min_break) // (total_breaks-2))
    breaks = []
    
    # Add minimum extreme
    breaks.append((-100, f"Under {min_break}{units}"))
    
    # Build the breaks
    for upper_bound in range(min_break, max_break, step):
        if upper_bound == 0:
            breaks.append((upper_bound, zero_break))
            continue
        breaks.append((upper_bound, f"{upper_bound+step}{units} to {upper_bound}{units}"))
        
    # Add maximum extreme
    breaks.append((100, f"Over {max_break}{units}"))
    
    return breaks


def main():
    # Placeholder symbology and color ramp
    project: ArcGISProject = ArcGISProject(r"<path_to_project>")
    raster_layer: Layer = project.listMaps('<map_name>')[0].listLayers('<raster_layer_name>')[0]
    
    layer_cim: CIMRasterLayer = raster_layer.getDefinition('V3')
    
    # Build the class breaks
    class_breaks = [CIMRasterClassBreak() for _ in range(10)]
    for (val, label), class_break in zip(build_breaks(-40, 40, 10), class_breaks):
        class_break: CIMRasterClassBreak = class_break
        class_break.label = label
        class_break.upperBound = val
    
    # Build the colorizer
    colorizer = CIMRasterClassifyColorizer()
    colorizer.classificationMethod = ClassificationMethod.Manual
    colorizer.classBreaks = class_breaks
    colorizer.field = "Value"
    
    layer_cim.colorizer.__dict__.update(colorizer.__dict__)
    raster_layer.setDefinition(layer_cim)
    
    raster_sym: Symbology = raster_layer.symbology
    sym_colorizer: RasterClassifyColorizer = raster_sym.colorizer
    color_ramp: ColorRamp = project.listColorRamps('Prediction')[0]
    sym_colorizer.colorRamp = color_ramp
    
    raster_layer.symbology = sym_colorizer
        
    # Save the project
    project.save()
    
if __name__ == '__main__':
    main()