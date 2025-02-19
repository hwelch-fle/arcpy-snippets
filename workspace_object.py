from __future__ import annotations

from collections import UserList
from typing import (
    overload, 
    Generator, 
    Literal,
    Callable,
)
from pathlib import Path
from contextlib import contextmanager

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
    def __init__(self, initlist=None):
        super().__init__(initlist)
        self.__flag = False # mangled flag for returning strings
        
    @overload
    def __getitem__(self, index: int) -> Path | str: ...
    @overload
    def __getitem__(self, name: str) -> Path | str: ...
    def __getitem__(self, ident: int | str) -> Path | str:
        if isinstance(ident, int):
            path = self.data[ident]
            return path if not self.__flag else str(path)
        elif isinstance(ident, str):
            for path in self.data:
                if path.name == ident:
                    return path if not self.__flag else str(path)
            raise KeyError(f"Path {ident} not found")
    
    @contextmanager
    def as_strings(self) -> Generator[PathList, None, None]:
        if not hasattr(self, '_as_string'):
            setattr(self, '_as_string', False)
        try:
            self.__flag = True
            yield self
        finally:
            self.__flag = False
    
class WorkspaceManager:
    # Caches are used to limit the amount of times
    # the List* functions are called, they tend to
    # be slow and if you run them in a loop it will
    # cause issues (around 1-2 seconds per `feature_classes` call)
    __caches__ = (
        '_datasets', 
        '_rasters',
        '_tables', 
        '_workspaces', 
        '_feature_classes', 
        '_files',
    )
    
    __slots__ = ('path', 'name', 'manager', *__caches__)
    
    def __init__(self, path: Path):
        self.path = Path(path)
        self.name = self.path.name
        self.manager = EnvManager(workspace=str(self.path))
        
        for cache in self.__caches__:
            setattr(self, cache, None)
    
    def _retrieve(self, func: Callable, cache: str) -> PathList:
        # Get cached paths
        if getattr(self, cache):
            return getattr(self, cache)
        
        # Get path using List* func
        with self.manager:
            items = func()
        setattr(self, cache, PathList(Path(self.path / item) for item in items))
        
        return getattr(self, cache)
    
    @property
    def datasets(self) -> PathList:
        return self._retrieve(ListDatasets, '_datasets')
    
    @property
    def rasters(self) -> PathList:
        return self._retrieve(ListRasters, '_rasters')
    
    @property
    def tables(self, wild_card: str=None, table_type: Literal['dBASE', 'INFO', 'ALL']=None) -> PathList:
        return self._retrieve(ListTables, '_tables')
    
    @property
    def workspaces(self) -> PathList:
        return self._retrieve(ListWorkspaces, '_workspaces')
    
    @property
    def feature_classes(self) -> PathList:
        if self._feature_classes:
            return self._feature_classes

        self._feature_classes = PathList()            
        for wsp in self.datasets + [self.path]:
            with EnvManager(workspace=str(wsp)):
                self._feature_classes.extend(
                    Path(self.path / item) for item in ListFeatureClasses())
        return self._feature_classes
    
    @property
    def files(self) -> PathList:
        return self._retrieve(ListFiles, '_files')
        
    def reload(self, caches: list[str]=None):
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
