# URLs of the feature services
fs1_url = "https://services-ap1.arcgis.com/xyzxyzxyzxyzx/arcgis/rest/services/featureservice1/FeatureServer/0"
fs2_url = "https://services-ap1.arcgis.com/xyzxyzxyzxyzx/arcgis/rest/services/featureservice2/FeatureServer/0"

import datetime
from arcgis.gis import GIS
from arcgis.features import (
    FeatureLayer, 
    Feature, 
)
from pandas import DataFrame
import certifi
import urllib3
import ssl
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Create a default SSL context with certificate verification
ssl_context = ssl.create_default_context(cafile=certifi.where())
http = urllib3.PoolManager(ssl_context=ssl_context)

# Make a request to verify the setup
response = http.request('GET', 'https://myorg.arcgis.com')
print("http response: " + str(response.status))

# Suppress only the single InsecureRequestWarning from urllib3 if necessary
warnings.simplefilter('ignore', InsecureRequestWarning)

# Create GIS object
print("Connecting to AGOL")
client_id = 'xyzxyzxyzxyzx'
client_secret = 'xyzxyzxyzxyzx'

gis = GIS("https://myorg.arcgis.com", client_id=client_id, client_secret=client_secret)
print("Logged in as: " + gis.properties.user.username)

# Access the feature layers
fs1_layer = FeatureLayer(fs1_url)
fs2_layer = FeatureLayer(fs2_url)

#def update_feature_services(fs1_layer, fs2_layer):
# Mapping of inspection_number values to field names in fs2
inspection_timeframes = [
    '2 weeks',   '4 weeks',   '6 weeks', 
    '8 weeks',   '10 weeks',  '12 weeks', 
    
    '4 months',  '5 months',  '6 months', 
    '9 months',  '12 months', '15 months', 
    '18 months', '21 months', '24 months',
]

# Because the field names are consistent, we can dynamically generate the mapping from the inspection_timeframes
inspection_mapping = {
    timeframe: f"insp_{timeframe.replace(' ', '_')}"
    for timeframe in inspection_timeframes
}

# Declare fields and where clause for fs1
out_fields = ['objectid', 'globalid', 'date_of_inspection', 'plantation', 'years_planted', 'username', 'inspection_number']
where_clause = "inspection_number <> 'Ad-hoc Inspection'"

# Pull fs1 as a DataFrame so we only need to iterate fs2
fs1_df: DataFrame = fs1_layer.query(where=where_clause, out_fields=out_fields, return_geometry=False, as_df=True)

# Query to get all features from fs2 without geometry
fs2_features: list[Feature] = fs2_layer.query(out_fields="*", return_geometry=False, as_df=True).features

# Flag for using the first feature if multiple matches are found
use_first = True

# Iterate through fs2 features and update the matching field
updates = []
for fs2_feature in fs2_features:
    fs2_attributes = fs2_feature.attributes
    
    # Get identifying attributes from fs2
    years_planted = fs2_attributes['PlantingYear']
    plantation = fs2_attributes['Plantation']
    
    print(f"\nPlantation: {plantation}, PYear: {years_planted}")
    
    # Skip if plantation or years_planted is empty, can't get a match without both
    if not plantation or not years_planted:
        print(f"\t[WARNING] {plantation=} | {years_planted=} for feature {fs2_attributes['OBJECTID']}")
        continue
    
    # Query fs1_df for the matching feature
    fs1_query = fs1_df.query(f"plantation == '{plantation}' and years_planted == {years_planted}")
    
    # Skip if no matching feature is found
    if fs1_query.empty:
        print(f"\t[WARNING] No match found for plantation {plantation} and planting year {years_planted}")
        continue
    
    # Warn if multiple matching features are found
    if len(fs1_query) > 1:
        print(f"\t[WARNING] Multiple features found for plantation {plantation} and planting year {years_planted}")
        if not use_first:
            print("\t[WARNING] Skipping feature")
            continue
    
    # Get the matching feature
    fs1_feature = fs1_query.iloc[0]
    inspection_number = fs1_feature['inspection_number']
    username = fs1_feature['username']
    inspection_date = datetime.datetime.fromtimestamp(fs1_feature['date_of_inspection'] / 1000).strftime("%Y/%m/%d")
    
    # Skip if the field name is not found (Use walrus operator to assign and check in one operation)
    # NOTE: .get() will raise an error if the key is not found, so we set a default value of None
    if not (field_name := inspection_mapping.get(inspection_number, None)):
        continue
    
    # Skip if the field is already populated
    if fs2_attributes[field_name]:
        continue
    
    print(f"\n\tPlantation: {fs2_attributes['Plantation']}, PYear: {fs2_attributes['PlantingYear']}, Inspection: {inspection_number}, User: {username}")
    print(f"\tChecking {username} on {inspection_date}")
    
    # Update the matching field with 'username on date' text
    print(f"\tInspection: {field_name}")
    fs2_attributes[field_name] = f"{username} on {inspection_date}"
    updates.append(fs2_feature)
    print(f"\tUpdated {username} on {inspection_date}")

if updates:
    print(f"\tApplying updates for {len(updates)} features")
    fs2_layer.edit_features(updates=updates)