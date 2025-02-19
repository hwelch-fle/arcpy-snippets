from time import perf_counter

from arcpy.da import SearchCursor, InsertCursor
from arcpy.management import Append, GetCount

def test_cursor(source: str, target: str) -> None:
    with SearchCursor(source, 'OID@') as cur:
        source_fields = cur.fields
    with SearchCursor(target, 'OID@') as cur:
        target_fields = cur.fields
        
    field_map = ['OID@', 'SHAPE@'] + list(set(source_fields) & set(target_fields))
    with InsertCursor(target, field_map) as cur:
        for row in SearchCursor(source, field_map):
            cur.insertRow(row)
            
def test_append(source: str, target: str) -> None:
    Append(source, target, 'NO_TEST')

if __name__ == '__main__':
    source = r'<Path to Feature Class>'
    target1 = r'<Path to Cursor Target>'
    target2 = r'<Path to Append Target>'
    
    feature_count = int(GetCount(source).getOutput(0))
    
    start = perf_counter()
    test_cursor(source, target1)
    end = perf_counter()
    cursor_per_row = (end - start)/feature_count
    print(f'Cursor: {cursor_per_row:.6f} seconds/row')
    
    start = perf_counter()
    test_append(source, target2)
    end = perf_counter()
    append_per_row = (end - start)/feature_count
    print(f'Append: {append_per_row:.6f} seconds/row')
    
    print(f'Cursor is {append_per_row/cursor_per_row:.2f} times faster than Append')