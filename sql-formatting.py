"""A Simple query formatter that takes a field and comparison set

Usage:
    >>> query = SQLQuery('inspection_number')
    >>> out_fields = ['objectid', 'globalid', 'date_of_inspection', ...]
    >>> fs1_features = fs1_layer.query(
    ...    where=(query + 'Ad-hoc Inspection').exclusive, 
    ...    out_fields=out_fields, 
    ...    return_geometry=False).features
    
    >>> query
    SQLQuery(self.field='inspection_number', self.comparisons=set())
    
    >>> (query + 'Ad-hoc Inspection').exclusive
    "inspection_number <> 'Ad-hoc Inspection'"
    
    >>> (query + 'Ad-hoc Inspection' + 'Other').exclusive
    "inspection_number NOT IN ('Ad-hoc Inspection','Other')"
    
    >>> (query + 'Ad-hoc Inspection' + 'Other').inclusive
    "inspection_number IN ('Ad-hoc Inspection','Other')"
"""

from __future__ import annotations

class SQLQuery:
    def __init__(self, field: str, comparisons: set=None):
        self.field = field
        if ' ' in field:
            self.field = f'"{field}"' # Wrap spaced field in ""
        self.comparisons = comparisons
        if not comparisons:
            self.comparisons = set() # initialize empty set
    
    def _guard(self, value: str | int | float) -> str | int | float | None:
        """Reject any non standard inputs, add single quotes to strings
        NOTE: This does not sanitize the input! Someone could still inject SQL queries
        into a string value.
        """
        if isinstance(value, str):
            value = f"'{value}'"
        elif not isinstance(value, int | float):
            raise ValueError(f"Invalid Comparison {value}, must be str | int | float")
        if value in self.comparisons:
            value = None
        return value
               
    def __add__(self, value: str | int | float) -> SQLQuery:
        comps = set(self.comparisons)
        comps.add(self._guard(value))
        return SQLQuery(self.field, comps)
    
    def __sub__(self, value: str | int | float) -> SQLQuery:
        comps = set(self.comparisons)
        comps.remove(self._guard(value))
        return SQLQuery(self.field, comps)
    
    def append(self, value: str | int | float) -> None:
        self.comparisons.add(self._guard(value))
    
    def extend(self, comparisons: list) -> None:
        for value in comparisons:
            self.comparisons.add(self._guard(value))
    
    def __repr__(self) -> str:
        return f"SQLQuery({self.field=}, {self.comparisons=})"
    
    def _compare(self, inclusive: bool):
        # No comparison returns all
        if not self.comparisons:
            return "1 = 1"
        
        # Use single op for one comparison
        if len(self.comparisons) == 1:
            return f"{self.field} {'=' if inclusive else '<>'} {list(self.comparisons)[0]}"
        
        # Use IN operator for multiple comparisons
        if len(self.comparisons) > 1:
            return f"{self.field} {'IN' if inclusive else 'NOT IN'} ({','.join(map(str, self.comparisons))})"
        
    @property
    def inclusive(self) -> str:
        return self._compare(inclusive=True)
    
    @property
    def exclusive(self) -> str:
        return self._compare(inclusive=False)