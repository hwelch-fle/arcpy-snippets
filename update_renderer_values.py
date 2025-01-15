from typing import Literal, TypeAlias, Union

from arcpy.mp import ArcGISProject
from arcpy._renderer import Base_renderer, UniqueValueRenderer, SimpleRenderer, Graduated_colors_renderer, Unclassed_colors_renderer, Graduated_symbols_renderer
from arcpy._symbology import Symbology, ItemGroup, Item
from arcpy._mp import Layer, Map

RendererName: TypeAlias = Literal[
    'GraduatedColorsRenderer', 
    'GraduatedSymbolsRenderer',
    'UnclassedColorsRenderer',
    'SimpleRenderer',
    'UniqueValueRenderer']

RendererType: TypeAlias = Union[
    Base_renderer, 
    UniqueValueRenderer,
    SimpleRenderer,
    Graduated_colors_renderer,
    Unclassed_colors_renderer,
    Graduated_symbols_renderer]

def get_symbology(layer: Layer) -> Symbology:
    return layer.symbology

def get_renderer(symbology: Symbology) -> RendererType:
    return symbology.renderer

def set_renderer(symbology: Symbology, renderer: RendererName) -> RendererType:
    symbology._updateRenderer(renderer)
    return get_renderer(symbology)

def get_unique_value_renderer_values(renderer: UniqueValueRenderer) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    groups: list[ItemGroup] = renderer.groups
    for group in groups:
        items: list[Item] = group.items
        values[group.heading] = [item.label for item in items]
    return values

def remove_all_values(renderer: UniqueValueRenderer):
    renderer.removeValues(get_unique_value_renderer_values(renderer))

def add_values(renderer: UniqueValueRenderer, values: dict[str, list[str]]) -> dict[str, list[str]]:
    return renderer.addValues(values) or values

def main():
    project = ArcGISProject(r"Path\To\Project")
    _map: Map = project.listMaps()[0]
    layer: Layer = _map.listLayers()[0]
    
    symbology = get_symbology(layer)
    renderer: UniqueValueRenderer = set_renderer(symbology, 'UniqueValueRenderer')
    remove_all_values(renderer)
    new_values = {}
    
    add_values(renderer, new_values)
    
    project.save()
    return

if __name__ == "__main__":
    main()