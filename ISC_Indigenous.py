import pandas as pd
import re

isc_csv = r"C:\water_advisory_map_data.csv"
out_csv = r"C:\Downloads\water_advisory_map_data_Full.csv"
out_points_csv = r"C:\ISC_advisory_points_ON_SK.csv"

df = pd.read_csv(isc_csv)

# Keep Ontario and Saskatchewan only
df["Region_clean"] = df["Region"].astype(str).str.upper().str.strip()

df_on_sk = df[df["Region_clean"].isin(["ONTARIO", "SASKATCHEWAN"])].copy()

# Determine whether each advisory record is active or lifted


def advisory_status(date_lifted):
    if pd.isna(date_lifted) or str(date_lifted).strip() == "":
        return "Active LT-DWA"
    else:
        return "Lifted LT-DWA"


df_on_sk["Water_Record_Status"] = df_on_sk["Date Advisory Lifted"].apply(
    advisory_status)

# Clean First Nation names for joining


def clean_name(x):
    if pd.isna(x):
        return ""
    x = str(x).upper().strip()
    x = x.replace(" FIRST NATION", "")
    x = x.replace(" FN", "")
    x = x.replace(".", "")
    x = x.replace(",", "")
    x = x.replace("’", "'")
    x = re.sub(r"\s+", " ", x)
    return x.strip()


df_on_sk["JOIN_NAME"] = df_on_sk["First Nation"].apply(clean_name)

# Save advisory points too, useful for QA/QC in ArcGIS
df_on_sk.to_csv(out_points_csv, index=False, encoding="utf-8-sig")

# Aggregate to one row per First Nation
records = []

for join_name, g in df_on_sk.groupby("JOIN_NAME"):

    has_active = (g["Water_Record_Status"] == "Active LT-DWA").any()
    has_lifted = (g["Water_Record_Status"] == "Lifted LT-DWA").any()

    if has_active:
        final_class = "Active LT-DWA"
    elif has_lifted:
        final_class = "Lifted LT-DWA record"
    else:
        final_class = "Other ISC advisory record"

    records.append({
        "JOIN_NAME": join_name,
        "First_Nation_ISC": g["First Nation"].iloc[0],
        "Water_Class": final_class,
        "Active_Advisory_Count": int((g["Water_Record_Status"] == "Active LT-DWA").sum()),
        "Lifted_Advisory_Count": int((g["Water_Record_Status"] == "Lifted LT-DWA").sum()),
        "Total_Advisory_Records": len(g),
        "Advisory_Types": "; ".join(sorted(g["Type of advisory"].dropna().astype(str).unique())),
        "Water_Systems": "; ".join(sorted(g["Water System Name"].dropna().astype(str).unique())[:5])
    })

out = pd.DataFrame(records)
out.to_csv(out_csv, index=False, encoding="utf-8-sig")

print("Saved:", out_csv)
print("Saved advisory points:", out_points_csv)
print(out.head())
