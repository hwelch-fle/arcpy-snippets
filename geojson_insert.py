import arcpy
from osgeo import ogr
import json

tbl =r"...\Default.gdb\work"
source = r"filepath"
spat_ref = arcpy.SpatialReference(102962)
in_ds = ogr.Open(source)
lay = in_ds.ExecuteSQL("select * from Townships")

# Do the risky processing outside the cursor so
# if something goes wrong, you wont have a partial insert
to_insert = []
for l in lay:
    # Load Geojson
    gJSON = json.loads(l.GetGeometryRef().ExportToJson())
    
    # Get as ESRI shape
    shape = arcpy.AsShape(gJSON)
    
    # Re-build shape with correct spatial reference
    proj_shape = arcpy.Polygon(arcpy.Array(part for part in shape), spat_ref)
    
    # Add shape to insert list
    to_insert.append(proj_shape)

with arcpy.da.InsertCursor(tbl, ["SHAPE@"]) as cursor:
    for proj_shape in to_insert:
        cursor.insertRow([proj_shape])