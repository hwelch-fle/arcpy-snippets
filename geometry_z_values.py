import arcpy
import os
from tempfile import mkdtemp

import arcpy.typing
import arcpy.typing.describe

# Create a file geodatabase
output_folder = mkdtemp("_geo-z-val_test")
gdb_name = "ExampleDatabase.gdb"
gdb_full_path = os.path.join(output_folder, gdb_name)

if not arcpy.Exists(gdb_full_path):
    arcpy.management.CreateFileGDB(out_folder_path=output_folder, out_name=gdb_name)

# Create a polyline feature class
feature_class_name_polyline = "counties_polyline"
arcpy.CreateFeatureclass_management(
    out_path=gdb_full_path,
    out_name=feature_class_name_polyline,
    geometry_type="POLYLINE",
    has_z="ENABLED"  # Enable Z values
)

# Create polyline geometry with Z values
array_polyline = arcpy.Array([arcpy.Point(1000.0, 2000.0, 50.0),
                               arcpy.Point(1500.0, 2500.0, 75.0),
                               arcpy.Point(2000.0, 3000.0, 100.0)])
polyline = arcpy.Polyline(array_polyline)

# InsertCursor to add new polyline geometry
with arcpy.da.InsertCursor(os.path.join(gdb_full_path, feature_class_name_polyline), ['SHAPE@']) as cursor:
    cursor.insertRow([polyline])

# Create a polygon feature class
feature_class_name_polygon = "counties_polygon"
res = arcpy.CreateFeatureclass_management(
    out_path=gdb_full_path,
    out_name=feature_class_name_polygon,
    geometry_type="POLYGON",
    has_z="ENABLED"  # Enable Z values
)

desc: 'arcpy.typing.describe.FeatureClass' = arcpy.Describe(res[0])
print(desc.hasZ)

# Create polygon geometry with Z values
array_polygon = arcpy.Array([arcpy.Point(1000.0, 2000.0, 50.0),
                              arcpy.Point(1500.0, 2000.0, 50.0),
                              arcpy.Point(1500.0, 2500.0, 50.0),
                              arcpy.Point(1000.0, 2500.0, 50.0),
                              arcpy.Point(1000.0, 2000.0, 50.0)])  # Closing the polygon
polygon = arcpy.Polygon(array_polygon, has_z=True)

for part in polygon:
    for point in part:
        print(point)

# InsertCursor to add new polygon geometry
with arcpy.da.InsertCursor(os.path.join(gdb_full_path, feature_class_name_polygon), ['SHAPE@']) as cursor:
    cursor.insertRow([polygon])

# Check Z values for polyline
with arcpy.da.SearchCursor(os.path.join(gdb_full_path, feature_class_name_polyline), ['SHAPE@']) as cursor:
    for row in cursor:
        geometry = row[0]
        for part in geometry:
            for p in part:
                print("Polyline - X:", p.X, "Y:", p.Y, "Z:", p.Z)  # Output Z values

# Check Z values for polygon
with arcpy.da.SearchCursor(os.path.join(gdb_full_path, feature_class_name_polygon), ['SHAPE@']) as cursor:
    for row in cursor:
        geometry = row[0]
        for part in geometry:
            for p in part:
                print("Polygon - X:", p.X, "Y:", p.Y, "Z:", p.Z)  # Output Z values