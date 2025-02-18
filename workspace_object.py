from __future__ import annotations

from collections import UserList
from typing import overload
from pathlib import Path

from arcpy import (
    EnvManager,
    ListDatasets,
    ListRasters,
    ListTables,
    ListWorkspaces,
    ListFeatureClasses,
    ListFiles,
)

class PathList(UserList[Path]):
    """A list of features that can be accessed by index or name"""
    
    @overload
    def __getitem__(self, index: int) -> Path: ...
    @overload
    def __getitem__(self, name: str) -> Path: ...
    def __getitem__(self, ident: int | str) -> Path:
        if isinstance(ident, int):
            return self.data[ident]
        elif isinstance(ident, str):
            for item in self.data:
                if item.name == ident:
                    return item
            raise KeyError(f"Item {ident} not found")
    
    def as_strings(self) -> list[str]:
        """Returns the list of paths as strings"""
        return [str(item) for item in self.data]
    
class WorkspaceManager:
    # Caches are used to limit the amount of times
    # the List* functions are called, they tend to
    # be slow and if you run them in a loop it will
    # be very slow (like 1-2 seconds per feature_classes)
    __caches__ = (
        '_datasets', 
        '_rasters',
        '_tables', 
        '_workspaces', 
        '_feature_classes', 
        '_files',
    )
    
    __slots__ = ('path', 'name', *__caches__)
    
    def __init__(self, path: Path):
        self.path = Path(path)
        self.name = self.path.name
        
        for cache in self.__caches__:
            setattr(self, cache, None)
    
    def _retrieve(self, func: callable, cache: str):
        if getattr(self, cache):
            return getattr(self, cache)
        
        with EnvManager(workspace=str(self.path)):
            items = func()
        setattr(self, cache, PathList(Path(self.path / item) for item in items))
        
        return getattr(self, cache)
    
    @property
    def datasets(self) -> PathList[Path]:
        return self._retrieve(ListDatasets, '_datasets')
    
    @property
    def rasters(self) -> PathList[Path]:
        return self._retrieve(ListRasters, '_rasters')
    
    @property
    def tables(self) -> PathList[Path]:
        return self._retrieve(ListTables, '_tables')
    
    @property
    def workspaces(self) -> PathList[Path]:
        return self._retrieve(ListWorkspaces, '_workspaces')
    
    @property
    def feature_classes(self) -> PathList[Path]:
        
        # Early return on cache hit
        if self._feature_classes:
            return self._feature_classes

        # retrieve datasets and root feature classes
        self._retrieve(ListDatasets, '_datasets')
        self._retrieve(ListFeatureClasses, '_feature_classes')
        
        # Return root feature classes if no datasets
        if not self.datasets:
            return self._feature_classes
        
        # Extend feature classes with datasets
        for ds in self.datasets:
            with EnvManager(workspace=str(ds)):
                self._feature_classes.extend(self.path / fc for fc in ListFeatureClasses())
        return self._feature_classes
        
    @property
    def files(self) -> PathList[Path]:
        return self._retrieve(ListFiles, '_files')
        
    def reload(self, caches: list[str] = None):
        """Reloads the caches for the workspace
        
        Args:
            caches: A list of caches to reload. If None, all caches are reloaded
        """
        if not caches:
            caches = self.__caches__
        
        for cache in caches:
            if not cache.startswith('_'):
                cache = f"_{cache}"
                
            if cache in self.__caches__:
                setattr(self, cache, None)


# Usage
"""
>>> workspace = WorkspaceManager(r"C:\path\to\workspace.gdb")
>>> print(workspace.name)
workspace.gdb

>>> print(workspace.feature_classes)
[Path('C:\path\to\workspace.gdb\feature_class1'), Path('C:\path\to\workspace.gdb\feature_class2')]

>>> for fc in workspace.feature_classes.as_strings():
...     print(fc)
C:\path\to\workspace.gdb\feature_class1
C:\path\to\workspace.gdb\feature_class2

>>> arcpy.management.CopyFeatures(workspace.feature_classes.as_strings()[0], str(workspace.path / 'copy_of_feature_class1'))
>>> workspace.feature_classes
[Path('C:\path\to\workspace.gdb\feature_class1'), Path('C:\path\to\workspace.gdb\feature_class2')]

>>> workspace.reload(['feature_classes'])
>>> workspace.feature_classes
[Path('C:\path\to\workspace.gdb\feature_class1'), Path('C:\path\to\workspace.gdb\feature_class2'), Path('C:\path\to\workspace.gdb\copy_of_feature_class1')]
"""