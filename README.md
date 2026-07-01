 GIS Indigenous Water

This repository contains two Python scripts used to get registered population and long-term drinking-water advisory status in Canada.

The workflow combines:

1. First Nations point locations exported from ArcGIS Pro
2. registered population data from First Nation Profiles
3. long-term drinking-water advisory records from Indigenous Services Canada (ISC)

---

Recommended GIS workflow:

1. Download the First Nations Location dataset, or add the official service/layer to ArcGIS Pro.
2. Open it in ArcGIS Pro.
3. Export the point attribute table to CSV.
4. Save it as:


C:\FN_points.csv


The CSV must contain a band-number field. The script will accept any of these field names:


BAND_NUMBER
BAND_NBR
BAND_NUMBE
BAND_NO
BANDNUMBER


Recommended fields to keep:


BAND_NBR
BAND_NAME
Latitude / Longitude or geometry fields if available



 Input B — water_advisory_map_data.csv

This file comes from the ISC map of lifted and active long-term drinking-water advisories.

Source dataset:


Map of lifted and active drinking water advisories - Indigenous Services Canada
https://www.sac-isc.gc.ca/eng/1620925418298/1620925434679


Recommended download workflow:

1. Open the ISC map page.
2. Click Download map data.
3. Save the downloaded CSV as:


C:\water_advisory_map_data.csv


The advisory CSV should include fields such as:


Region
First Nation
Water System Name
Type of advisory
Date Advisory Set
Long term advisory since
Date Advisory Lifted
Project Phase
Population
Corrective Measure
Longitude
Latitude




 4. Run the population script

Run:

bash
python Population_Indigenous.py


This script:

1. reads FN_points.csv
2. detects the band-number field
3. loops through each unique band number
4. queries the First Nation Profiles registered-population page
5. extracts:
   - official name
   - population date
   - total registered population
   - registered population on own reserve
   - registered population off reserve
6. writes:


C:\FN_registered_population.csv


Expected output fields:


BAND_NBR
Official_Name_Profile
Population_Date
Total_Registered_Population
Registered_On_Own_Reserve
Registered_Off_Reserve
Source_URL
Status


---

 5. Run the ISC advisory script

Run:

bash
python ISC_Indigenous.py


This script:

1. reads water_advisory_map_data.csv
2. keeps only Ontario and Saskatchewan records
3. classifies each advisory record as:
   - Active LT-DWA if Date Advisory Lifted is blank
   - Lifted LT-DWA if Date Advisory Lifted is populated
4. creates a cleaned join field called JOIN_NAME
5. aggregates records to one row per First Nation
6. writes two outputs:


C:\Downloads\water_advisory_map_data_Full.csv
C:\ISC_advisory_points_ON_SK.csv


Main output table:


water_advisory_map_data_Full.csv


Expected fields:


JOIN_NAME
First_Nation_ISC
Water_Class
Active_Advisory_Count
Lifted_Advisory_Count
Total_Advisory_Records
Advisory_Types
Water_Systems


The second output, ISC_advisory_points_ON_SK.csv, keeps the original advisory records and is useful for QA/QC or mapping advisory system locations.

---
