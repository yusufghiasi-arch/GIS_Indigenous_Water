import pandas as pd
import requests
import re
import time
import html
from pathlib import Path

# -------------------------------------------------
# Input / output
# -------------------------------------------------
points_csv = r"C:\FN_points.csv"
out_csv = r"C:\FN_registered_population.csv"

pts = pd.read_csv(points_csv)

# Your ArcGIS-exported field seems to be BAND_NBR
possible_cols = [
    c for c in pts.columns
    if c.upper() in ["BAND_NUMBER", "BAND_NBR", "BAND_NUMBE", "BAND_NO", "BANDNUMBER"]
]

if not possible_cols:
    raise ValueError("Could not find a band-number field. Check your CSV field names.")

band_col = possible_cols[0]
print("Using band field:", band_col)

bands = (
    pd.to_numeric(pts[band_col], errors="coerce")
    .dropna()
    .astype(int)
    .drop_duplicates()
    .sort_values()
    .tolist()
)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def clean_html_to_text(raw_html):
    """Convert HTML to plain searchable text without external packages."""
    txt = re.sub(r"<script.*?</script>", " ", raw_html, flags=re.S | re.I)
    txt = re.sub(r"<style.*?</style>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()

def extract_number_after_label(text, label):
    """
    Finds patterns like:
    Total Registered Population 411
    Registered Males On Own Reserve 112
    """
    pattern = re.escape(label) + r"\s+([0-9][0-9,]*)"
    m = re.search(pattern, text, flags=re.I)
    if not m:
        return None
    return int(m.group(1).replace(",", ""))

def extract_text_between(text, start_label, end_label):
    pattern = re.escape(start_label) + r"\s+(.*?)\s+" + re.escape(end_label)
    m = re.search(pattern, text, flags=re.I)
    if not m:
        return None
    return m.group(1).strip()

records = []

for i, band_number in enumerate(bands, start=1):

    url = (
        "https://fnp-ppn.aadnc-aandc.gc.ca/fnp/Main/Search/"
        f"FNRegPopulation.aspx?BAND_NUMBER={band_number}&lang=eng"
    )

    print(f"{i}/{len(bands)} - BAND_NBR {band_number}")

    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()

        text = clean_html_to_text(r.text)

        official_name = extract_text_between(text, "Official Name", "Number")

        total_pop = extract_number_after_label(text, "Total Registered Population")

        male_own = extract_number_after_label(text, "Registered Males On Own Reserve") or 0
        female_own = extract_number_after_label(text, "Registered Females On Own Reserve") or 0
        on_own_reserve = male_own + female_own

        male_off = extract_number_after_label(text, "Registered Males Off Reserve") or 0
        female_off = extract_number_after_label(text, "Registered Females Off Reserve") or 0
        off_reserve = male_off + female_off

        # Optional: population date, e.g. "Registered Population as of May, 2026"
        date_match = re.search(r"Registered Population as of\s+([A-Za-z]+,\s+\d{4})", text)
        pop_date = date_match.group(1) if date_match else None

        status = "OK" if total_pop is not None else "Population not found"

        records.append({
            "BAND_NBR": band_number,
            "Official_Name_Profile": official_name,
            "Population_Date": pop_date,
            "Total_Registered_Population": total_pop,
            "Registered_On_Own_Reserve": on_own_reserve,
            "Registered_Off_Reserve": off_reserve,
            "Source_URL": url,
            "Status": status
        })

        time.sleep(0.2)

    except Exception as e:
        records.append({
            "BAND_NBR": band_number,
            "Official_Name_Profile": None,
            "Population_Date": None,
            "Total_Registered_Population": None,
            "Registered_On_Own_Reserve": None,
            "Registered_Off_Reserve": None,
            "Source_URL": url,
            "Status": f"Error: {e}"
        })

pop = pd.DataFrame(records)
pop.to_csv(out_csv, index=False, encoding="utf-8-sig")

print("Saved:", out_csv)
