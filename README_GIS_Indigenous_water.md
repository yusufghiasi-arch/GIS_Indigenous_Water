# GIS Indigenous Water

This repository contains two Python scripts used to prepare GIS-ready tables for mapping First Nations registered population and long-term drinking-water advisory status in Ontario and Saskatchewan.

The workflow combines:

1. First Nations point locations exported from ArcGIS Pro
2. registered population data from First Nation Profiles
3. long-term drinking-water advisory records from Indigenous Services Canada (ISC)

The final outputs can be joined in ArcGIS Pro or QGIS and symbolized as:

- circle size = total registered population
- circle colour = long-term drinking-water advisory status

---

## Repository files

| File | Purpose |
|---|---|
| `Population_Indigenous.py` | Reads a First Nations point CSV containing `BAND_NBR`/`BAND_NUMBER`, queries First Nation Profiles pages, and creates a registered-population CSV. |
| `ISC_Indigenous.py` | Reads ISC drinking-water advisory map data, filters Ontario and Saskatchewan, standardizes First Nation names, and creates a water-advisory status table. |

---

## 1. Python setup

Create or use a Python environment with:

```bash
python -m pip install pandas requests
```

The scripts also use standard Python libraries:

```text
re
time
html
pathlib
```

No `html5lib` or `BeautifulSoup` is required.

---

## 2. Required input files

Before running the scripts, prepare these two input CSV files.

---

### Input A — `FN_points.csv`

This file comes from the official First Nations location point dataset.

Source dataset:

```text
First Nations Location - Open Government Portal
https://open.canada.ca/data/en/dataset/b6567c5c-8339-4055-99fa-63f92114d9e4
```

Recommended GIS workflow:

1. Download the First Nations Location dataset, or add the official service/layer to ArcGIS Pro.
2. Open it in ArcGIS Pro.
3. Export the point attribute table to CSV.
4. Save it as:

```text
C:\FN_points.csv
```

The CSV must contain a band-number field. The script will accept any of these field names:

```text
BAND_NUMBER
BAND_NBR
BAND_NUMBE
BAND_NO
BANDNUMBER
```

Recommended fields to keep:

```text
BAND_NBR
BAND_NAME
Latitude / Longitude or geometry fields if available
```

The population script only needs the band-number field, but `BAND_NAME` is useful later in GIS.

---

### Input B — `water_advisory_map_data.csv`

This file comes from the ISC map of lifted and active long-term drinking-water advisories.

Source dataset:

```text
Map of lifted and active drinking water advisories - Indigenous Services Canada
https://www.sac-isc.gc.ca/eng/1620925418298/1620925434679
```

Recommended download workflow:

1. Open the ISC map page.
2. Click `Download map data`.
3. Save the downloaded CSV as:

```text
C:\water_advisory_map_data.csv
```

The advisory CSV should include fields such as:

```text
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
```

---

## 3. Edit paths if needed

Both scripts currently use hard-coded Windows paths.

In `Population_Indigenous.py`:

```python
points_csv = r"C:\FN_points.csv"
out_csv = r"C:\FN_registered_population.csv"
```

In `ISC_Indigenous.py`:

```python
isc_csv = r"C:\water_advisory_map_data.csv"
out_csv = r"C:\Downloads\water_advisory_map_data_Full.csv"
out_points_csv = r"C:\ISC_advisory_points_ON_SK.csv"
```

Either place the input files exactly at those paths, or edit the paths before running.

---

## 4. Run the population script

Run:

```bash
python Population_Indigenous.py
```

This script:

1. reads `FN_points.csv`
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

```text
C:\FN_registered_population.csv
```

Expected output fields:

```text
BAND_NBR
Official_Name_Profile
Population_Date
Total_Registered_Population
Registered_On_Own_Reserve
Registered_Off_Reserve
Source_URL
Status
```

---

## 5. Run the ISC advisory script

Run:

```bash
python ISC_Indigenous.py
```

This script:

1. reads `water_advisory_map_data.csv`
2. keeps only Ontario and Saskatchewan records
3. classifies each advisory record as:
   - `Active LT-DWA` if `Date Advisory Lifted` is blank
   - `Lifted LT-DWA` if `Date Advisory Lifted` is populated
4. creates a cleaned join field called `JOIN_NAME`
5. aggregates records to one row per First Nation
6. writes two outputs:

```text
C:\Downloads\water_advisory_map_data_Full.csv
C:\ISC_advisory_points_ON_SK.csv
```

Main output table:

```text
water_advisory_map_data_Full.csv
```

Expected fields:

```text
JOIN_NAME
First_Nation_ISC
Water_Class
Active_Advisory_Count
Lifted_Advisory_Count
Total_Advisory_Records
Advisory_Types
Water_Systems
```

The second output, `ISC_advisory_points_ON_SK.csv`, keeps the original advisory records and is useful for QA/QC or mapping advisory system locations.

---

## 6. ArcGIS Pro / QGIS workflow after running scripts

### Step 1 — Join population to First Nations points

In ArcGIS Pro:

1. Add the First Nations point layer.
2. Add `FN_registered_population.csv`.
3. Join by:

```text
Point layer field: BAND_NBR
Population table field: BAND_NBR
```

4. Export the joined layer as a permanent feature class.

Suggested name:

```text
FirstNations_Population
```

---

### Step 2 — Create `JOIN_NAME` in the joined point layer

Create a text field:

```text
JOIN_NAME
```

Calculate it using the same cleaning logic as the ISC script:

```python
import re

def clean_name(x):
    if x is None:
        return ""
    x = str(x).upper().strip()
    x = x.replace(" FIRST NATION", "")
    x = x.replace(" FN", "")
    x = x.replace(".", "")
    x = x.replace(",", "")
    x = x.replace("’", "'")
    x = re.sub(r"\s+", " ", x)
    return x.strip()
```

Expression:

```python
clean_name(!BAND_NAME!)
```

---

### Step 3 — Join water advisory status

Add:

```text
water_advisory_map_data_Full.csv
```

Join by:

```text
Point layer field: JOIN_NAME
Water advisory table field: JOIN_NAME
```

Export the joined layer as:

```text
FirstNations_Population_WaterClass
```

---

### Step 4 — Fill missing advisory classes

Some First Nations will not have a matching long-term advisory record in the ISC table. That does not mean the community has safe water; it only means no matching LT-DWA record was found in the ISC dataset used here.

Create a text field:

```text
Water_Class_Final
```

Calculate it as:

```python
def final_class(x):
    if x is None or str(x).strip() == "":
        return "No LT-DWA record in ISC data"
    return str(x)
```

Expression:

```python
final_class(!Water_Class!)
```

---

## 7. Suggested map symbology

Recommended bivariate map design:

```text
circle size = Total_Registered_Population
circle colour = Water_Class_Final
```

Suggested water-advisory colours:

| Water class | Suggested colour |
|---|---|
| Active LT-DWA | Red |
| Lifted LT-DWA record | Orange |
| No LT-DWA record in ISC data | Blue or blue-gray |

Suggested population classes:

| Population class |
|---|
| < 500 |
| 500–1,500 |
| 1,500–3,000 |
| 3,000–6,000 |
| > 6,000 |

---

## 8. Important interpretation note

Use this note in maps, reports, or README text:

```text
Point locations represent First Nation administrative/community locations. Population refers to total registered population by First Nation. Advisory status reflects ISC long-term drinking-water advisory records for public systems on reserve where available. “No LT-DWA record” does not imply household-level water safety or absence of all water-quality concerns.
```

---

## 9. Output products

After the workflow, expected outputs include:

```text
FN_registered_population.csv
water_advisory_map_data_Full.csv
ISC_advisory_points_ON_SK.csv
FirstNations_Population_WaterClass
```

The final GIS layer can be used for mapping First Nations registered population and long-term drinking-water advisory status in Ontario and Saskatchewan.
