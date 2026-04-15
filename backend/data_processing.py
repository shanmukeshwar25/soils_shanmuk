# import pandas as pd
# import numpy as np
# import os
# import io
# import re

# DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis_data_09-04-2026_2(in).csv')

# # Helper to read poorly quoted CSVs where the entire row is quoted
# def _read_custom_csv(filepath: str) -> pd.DataFrame:
#     with open(filepath, 'r', encoding='utf-8') as f:
#         text = f.read()
#     if text.startswith('\ufeff'):
#         text = text[1:]
#     text = re.sub(r'(?m)^"|"$', '', text)
#     text = text.replace('""', '"')
#     return pd.read_csv(io.StringIO(text))

# # Global variable to hold the cached dataset
# _cleaned_data = None

# def _parse_dates(df, col_name, format_str=None):
#     if format_str:
#         return pd.to_datetime(df[col_name], format=format_str, errors='coerce')
#     else:
#         return pd.to_datetime(df[col_name], dayfirst=True, errors='coerce')

# def load_and_clean_data(csv_path: str) -> pd.DataFrame:
#     """Loads and preprocesses the soil dataset."""
#     df = _read_custom_csv(csv_path)
    
#     # Drop rows where critical Date columns are missing
#     df = df.dropna(subset=['CreatedDate', 'CropStartDate', 'CropEndDate', 'ValueS'])
    
#     # Convert dates
#     df['CreatedDate'] = pd.to_datetime(df['CreatedDate'], dayfirst=True, errors='coerce')
#     df['CropStartDate'] = pd.to_datetime(df['CropStartDate'], dayfirst=True, errors='coerce')
#     df['CropEndDate'] = pd.to_datetime(df['CropEndDate'], dayfirst=True, errors='coerce')
    
#     # Remove unparseable dates
#     df = df.dropna(subset=['CreatedDate', 'CropStartDate', 'CropEndDate'])
    
#     # Filter strictly within crop lifecycle
#     df = df[(df['CreatedDate'] >= df['CropStartDate']) & (df['CreatedDate'] <= df['CropEndDate'])]
    
#     # Clean up UnitS format and strictly keep only 'kg/ha' or 'g/ha' elements
#     df['UnitS'] = df['UnitS'].astype(str).str.lower().str.strip()
#     df = df[df['UnitS'].isin(['kg/ha', 'g/ha'])]
    
#     # Helper to calculate kg/ha precisely
#     def to_kgha(row):
#         try:
#             val = float(row['ValueS'])
#             u = row['UnitS']
#             if u == 'g/ha': return val / 1000.0
#             return val
#         except:
#             return 0.0

#     df['ValueS'] = df.apply(to_kgha, axis=1)
#     df['UnitS'] = 'kg/ha'
    
#     # Calculate days from start column
#     df['days_from_start'] = (df['CreatedDate'] - df['CropStartDate']).dt.days
    
#     # Rename for easier access
#     df = df.rename(columns={'Plant/Crop': 'Crop'})
    
#     # Keep BatchId to uniquely identify samples tested on the same date
#     if 'BatchId' not in df.columns:
#         df['BatchId'] = 'Unknown'
    
#     df['BatchId'] = df['BatchId'].fillna('Unknown')
    
#     # Aggregate to handle exact measure duplicates within the SAME batch
#     agg_df = df.groupby(['Crop', 'SoilType', 'CreatedDate', 'BatchId', 'CropStartDate', 'CropEndDate', 'Measure']).agg({
#         'ValueS': 'mean'
#     }).reset_index()
    
#     # Sort properly
#     agg_df = agg_df.sort_values(by='CreatedDate')
    
#     return agg_df

# def get_data() -> pd.DataFrame:
#     global _cleaned_data
#     if _cleaned_data is None:
#         _cleaned_data = load_and_clean_data(DATA_PATH)
#     return _cleaned_data

# def get_filters():
#     df = get_data()
#     return {
#         "crops": sorted(df['Crop'].dropna().unique().tolist()),
#         "soil_types": sorted(df['SoilType'].dropna().unique().tolist()),
#         "measures": sorted(df['Measure'].dropna().unique().tolist())
#     }

# def get_time_series_data(crop: str, soil: str):
#     df = get_data()
#     sub_df = df[(df['Crop'] == crop) & (df['SoilType'] == soil)]
    
#     if sub_df.empty:
#         return []
    
#     pivot_df = sub_df.pivot_table(
#         index=['CreatedDate', 'BatchId', 'CropStartDate', 'CropEndDate', 'Crop', 'SoilType'], 
#         columns='Measure', 
#         values='ValueS', 
#         aggfunc='first'
#     ).reset_index()
    
#     pivot_df = pivot_df.sort_values(['CreatedDate', 'BatchId'])
    
#     pivot_df['date'] = pivot_df.apply(
#         lambda row: f"{row['CreatedDate'].strftime('%Y-%m-%d %H:%M:%S')} (Batch {row['BatchId']})", 
#         axis=1
#     )
    
#     pivot_df['CropStartDate'] = pivot_df['CropStartDate'].dt.strftime('%Y-%m-%d')
#     pivot_df['CropEndDate'] = pivot_df['CropEndDate'].dt.strftime('%Y-%m-%d')
    
#     pivot_df = pivot_df.drop(columns=['CreatedDate', 'BatchId'])
#     pivot_df = pivot_df.replace({np.nan: None})
    
#     return pivot_df.to_dict(orient='records')

# def get_summary_stats(crop: str, soil: str):
#     df = get_data()
#     sub_df = df[(df['Crop'] == crop) & (df['SoilType'] == soil)]
    
#     if sub_df.empty:
#         return []
        
#     summary = []
#     for measure, group in sub_df.groupby('Measure'):
#         group_sorted = group.sort_values('CreatedDate')
#         last_val = float(group_sorted.iloc[-1]['ValueS'])
#         avg_val = float(group['ValueS'].mean())
#         min_val = float(group['ValueS'].min())
#         max_val = float(group['ValueS'].max())
        
#         summary.append({
#             "measure": measure,
#             "latest": last_val,
#             "average": avg_val,
#             "min": min_val,
#             "max": max_val,
#             "unit": 'kg/ha'
#         })
        
#     return summary

# def get_date_range(crop: str, soil: str):
#     """
#     Build Timeline Focus dropdown options grouped by calendar year of actual samples.

#     Logic:
#     - Read all rows for the given crop + soil combination.
#     - Extract the year from each row's CreatedDate (the actual sample date).
#     - Group rows by that year, computing min(CreatedDate) = first_sample
#       and max(CreatedDate) = last_sample within the year.
#     - Build a human-readable label: "Apr 2024 - Aug 2024"
#       (first sample month/year  to  last sample month/year in that year).
#     - Return one entry per year, sorted chronologically by first_sample.
#     - The frontend uses first_sample..last_sample as the inclusive filter bounds.
#     """
#     df_raw = _read_custom_csv(DATA_PATH)
#     df_raw['CreatedDate']   = pd.to_datetime(df_raw['CreatedDate'],   dayfirst=True, errors='coerce')
#     df_raw['CropStartDate'] = pd.to_datetime(df_raw['CropStartDate'], dayfirst=True, errors='coerce')
#     df_raw['CropEndDate']   = pd.to_datetime(df_raw['CropEndDate'],   dayfirst=True, errors='coerce')
#     df_raw = df_raw.rename(columns={'Plant/Crop': 'Crop'})

#     sub = df_raw[
#         (df_raw['Crop'] == crop) &
#         (df_raw['SoilType'] == soil)
#     ].dropna(subset=['CreatedDate'])

#     if sub.empty:
#         return {"windows": []}

#     # Group by the calendar year of the actual sample CreatedDate
#     sub = sub.copy()
#     sub['sample_year'] = sub['CreatedDate'].dt.year

#     yearly = (
#         sub.groupby('sample_year')['CreatedDate']
#         .agg(first_sample='min', last_sample='max')
#         .reset_index()
#         .sort_values('first_sample')
#     )

#     out = []
#     for _, row in yearly.iterrows():
#         fs = row['first_sample']
#         ls = row['last_sample']
#         # "Apr 2024 - Aug 2024"  (same year -> e.g. "Apr 2024 - Apr 2024" is fine too)
#         label = f"{fs.strftime('%b %Y')} - {ls.strftime('%b %Y')}"
#         out.append({
#             "label":        label,
#             "first_sample": fs.strftime('%Y-%m-%d %H:%M:%S'),
#             "last_sample":  ls.strftime('%Y-%m-%d %H:%M:%S'),
#             "year":         int(row['sample_year']),
#         })

#     return {"windows": out}


import pandas as pd
import numpy as np
import os
import io
import re

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis_data_09-04-2026_2(in).csv')

# ── Category classification ───────────────────────────────────────────────────
# Soil-related categories (fertilization, minerals, nutrients)
SOIL_CATEGORIES = {
    'N-min 0-90 cm',
    'pH + O.S.',
    'Verticilium onderzoek in grond',
    'Beschikbare voorraad N + K',
    'Stengelaaltjes',
    'Longidorus en Xiphinema',
    'N-Mineraal Totaal',
    'Bemesting uitgebreid 0-90 cm',
    'pH',
    'Aaltjes + 28 dgn incubatie'
}

PLANT_CATEGORIES = {
    'Drogestof onderzoek plant',
    'Drogestof onderzoek plant compleet',
    'Vruchtanalyse Plus',
    'Brix-waarde bepaling'
}

MIXED_CATEGORIES = {
    'Bemesting Uitgebreid',
    'Aaltjes + 14 dgn Incubatie',
    'In de teelt bemesting - BASIS',
    'Aaltjes + 14 dgn incubatie + Cystenonderzoek',
    'In de teelt bemesting - UITGEBREID',
    'Bemesting Basis',
    'Tussentijdse rapportage Aaltjes',
    'Bemesting Uitgebreid + Fosfaatdifferentiatie',
    'Aaltjes - Zonder incubatie',
    'In de teelt bemesting - CHECKMONSTER',
    'N-mineraal',
    'Zware Metalen',
    'Wateronderzoek',
    'Plantsap monsters',
    'Fosfaatdifferentiatie',
    'Derogatie (veehouderij)',
    'Mestonderzoek (vast/vloeibaar)',
    'Scheurmonster grasland',
    'Bemesting uitgebreid + Klei/Zand/Silt verhouding',
    'Vrijwillig AM onderzoek',
    'Bietencysten onderzoek grond',
    'Bemesting basis + EC',
    'Fosfaatdifferentiatie + pH',
    'E-coli wateronderzoek',
    'Aaltjes zonder incubatie + Cysten'
}

def classify_category(cat: str) -> str:
    """Returns 'soil', 'plant', or 'mixed' for a category string."""
    if cat in SOIL_CATEGORIES:
        return 'soil'
    if cat in PLANT_CATEGORIES:
        return 'plant'
    if cat in MIXED_CATEGORIES:
        return 'mixed'
        
    # Keyword fallback
    c = str(cat).lower()
    if any(k in c for k in ['bodem', 'grond', 'bemesting', 'ph', 'fosfaat', 'zand', 'klei', 'mineraal', 'ec', 'os', 'o.s.']):
        return 'soil'
    if any(k in c for k in ['plant', 'vrucht', 'gewas', 'sap', 'blad', 'brix', 'drogestof']):
        return 'plant'
        
    return 'mixed'

# Helper to read poorly quoted CSVs where the entire row is quoted
def _read_custom_csv(filepath: str) -> pd.DataFrame:
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    if text.startswith('\ufeff'):
        text = text[1:]
    text = re.sub(r'(?m)^"|"$', '', text)
    text = text.replace('""', '"')
    return pd.read_csv(io.StringIO(text))

# Global variable to hold the cached dataset
_cleaned_data = None

def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    """Loads and preprocesses the soil dataset."""
    df = _read_custom_csv(csv_path)

    # Drop rows where critical Date columns are missing
    df = df.dropna(subset=['CreatedDate', 'ValueS'])

    # Convert dates
    df['CreatedDate']   = pd.to_datetime(df['CreatedDate'],   dayfirst=True, errors='coerce')
    df['CropStartDate'] = pd.to_datetime(df['CropStartDate'], dayfirst=True, errors='coerce')
    df['CropEndDate']   = pd.to_datetime(df['CropEndDate'],   dayfirst=True, errors='coerce')

    # Remove unparseable CreatedDates
    df = df.dropna(subset=['CreatedDate'])

    # Clean up UnitS format
    df['UnitS'] = df['UnitS'].astype(str).str.strip()
    
    # Convert g/ha to kg/ha for standardization, leave other units alone (like %, index, mg/l)
    def standardize_val(row):
        try:
            val = float(row['ValueS'])
            u = str(row['UnitS']).lower()
            if u == 'g/ha':
                return val / 1000.0
            return val
        except:
            return 0.0

    df['ValueS'] = df.apply(standardize_val, axis=1)
    
    # Update unit labels for those converted
    df['UnitS'] = df['UnitS'].apply(lambda u: 'kg/ha' if str(u).lower() == 'g/ha' else str(u).lower())

    # Calculate days from start column (NaN if no crop cycle)
    df['days_from_start'] = (df['CreatedDate'] - df['CropStartDate']).dt.days

    # Rename for easier access
    df = df.rename(columns={'Plant/Crop': 'Crop'})

    # Keep BatchId to uniquely identify samples tested on the same date
    if 'BatchId' not in df.columns:
        df['BatchId'] = 'Unknown'
    df['BatchId'] = df['BatchId'].fillna('Unknown')

    # Ensure Category column exists
    if 'Category' not in df.columns:
        df['Category'] = 'Unknown'
    df['Category'] = df['Category'].fillna('Unknown')
    
    # Fill NAs to prevent groupby from dropping them
    df['Crop'] = df['Crop'].fillna('Unknown')
    df['SoilType'] = df['SoilType'].fillna('Unknown')
    df['CropStartDate'] = df['CropStartDate'].dt.strftime('%Y-%m-%d').fillna('Unknown')
    df['CropEndDate'] = df['CropEndDate'].dt.strftime('%Y-%m-%d').fillna('Unknown')
    df['days_from_start'] = df['days_from_start'].fillna(-999)

    # Compute HasPlantData / HasSoilData flags before aggregation
    df['HasPlantData'] = df['Crop'].notna().astype(int)
    df['HasSoilData']  = df['SoilType'].notna().astype(int)

    # Aggregate to handle exact measure duplicates within the SAME batch
    # Category, HasPlantData, HasSoilData are preserved
    agg_df = df.groupby([
        'Crop', 'SoilType', 'CreatedDate', 'BatchId',
        'CropStartDate', 'CropEndDate', 'Category', 'Measure', 'days_from_start'
    ]).agg({
        'ValueS':       'mean',
        'HasPlantData': 'max',
        'HasSoilData':  'max',
        'UnitS':        'first',
    }).reset_index()

    # Sort properly
    agg_df = agg_df.sort_values(by='CreatedDate')

    return agg_df


def get_data() -> pd.DataFrame:
    global _cleaned_data
    if _cleaned_data is None:
        _cleaned_data = load_and_clean_data(DATA_PATH)
    return _cleaned_data


def get_filters():
    df = get_data()
    return {
        "crops": ["All Crops"] + sorted(df['Crop'].replace('Unknown', pd.NA).dropna().unique().tolist()),
        "soil_types": ["All Soils"] + sorted(df['SoilType'].replace('Unknown', pd.NA).dropna().unique().tolist()),
        "measures": sorted(df['Measure'].dropna().unique().tolist()),
    }


def get_all_categories():
    """Returns all distinct categories with their type (soil/plant/other)."""
    df = get_data()
    all_cats = sorted(df['Category'].dropna().unique().tolist())
    return {
        "categories": [
            {"name": c, "type": classify_category(c)}
            for c in all_cats
        ],
        "soil_categories": sorted(SOIL_CATEGORIES),
        "plant_categories": sorted(PLANT_CATEGORIES),
    }


def get_categories(crop: str, soil: str, cat_type: str = None):
    """Returns distinct Category values for a given crop+soil combination, with type metadata."""
    df = get_data()
    sub = df.copy()
    if crop and crop != 'All Crops':
        sub = sub[sub['Crop'] == crop]
    if soil and soil != 'All Soils':
        sub = sub[sub['SoilType'] == soil]
    all_cats = sorted(sub['Category'].dropna().unique().tolist())
    categories = [
        {"name": c, "type": classify_category(c)}
        for c in all_cats
    ]
    if cat_type:
        categories = [c for c in categories if c["type"] == cat_type]
    return {
        "categories": categories
    }


def get_time_series_data(crop: str, soil: str, categories: str = None, cat_type: str = None):
    df = get_data()
    sub_df = df.copy()
    if crop and crop != 'All Crops':
        sub_df = sub_df[sub_df['Crop'] == crop]
    if soil and soil != 'All Soils':
        sub_df = sub_df[sub_df['SoilType'] == soil]

    if categories and categories != 'All':
        cats_list = [c.strip() for c in categories.split(',')]
        sub_df = sub_df[sub_df['Category'].isin(cats_list)]
    if cat_type:
        sub_df = sub_df[sub_df['Category'].apply(classify_category) == cat_type]

    if sub_df.empty:
        return []

    pivot_df = sub_df.pivot_table(
        index=['CreatedDate', 'BatchId', 'CropStartDate', 'CropEndDate', 'Crop', 'SoilType', 'days_from_start', 'Category'],
        columns='Measure',
        values='ValueS',
        aggfunc='first'
    ).reset_index()

    pivot_df = pivot_df.sort_values(['CreatedDate', 'BatchId'])

    pivot_df['date'] = pivot_df.apply(
        lambda row: f"{row['CreatedDate'].strftime('%Y-%m-%d %H:%M:%S')} (Batch {row['BatchId']})",
        axis=1
    )

    # CropStartDate and CropEndDate are already stringified in load_and_clean_data
    pivot_df = pivot_df.drop(columns=['CreatedDate', 'BatchId'])
    pivot_df = pivot_df.replace({np.nan: None, 'Unknown': None, -999.0: None, -999: None})

    return pivot_df.to_dict(orient='records')


def get_summary_stats(crop: str, soil: str, categories: str = None, cat_type: str = None):
    df = get_data()
    sub_df = df.copy()
    if crop and crop != 'All Crops':
        sub_df = sub_df[sub_df['Crop'] == crop]
    if soil and soil != 'All Soils':
        sub_df = sub_df[sub_df['SoilType'] == soil]

    if categories and categories != 'All':
        cats_list = [c.strip() for c in categories.split(',')]
        sub_df = sub_df[sub_df['Category'].isin(cats_list)]
    if cat_type:
        sub_df = sub_df[sub_df['Category'].apply(classify_category) == cat_type]

    if sub_df.empty:
        return []

    summary = []
    for (cat_name, measure), group in sub_df.groupby(['Category', 'Measure']):
        group_sorted = group.sort_values('CreatedDate')
        last_val = float(group_sorted.iloc[-1]['ValueS'])
        avg_val  = float(group['ValueS'].mean())
        min_val  = float(group['ValueS'].min())
        max_val  = float(group['ValueS'].max())
        
        # Determine actual unit, fall back to empty string if missing
        unit_val = 'Unknown'
        if 'UnitS' in group.columns and not group['UnitS'].empty:
            unit_val = str(group['UnitS'].iloc[0]).strip()
            # Clean weird units
            if unit_val.lower() == 'nan':
                unit_val = ''

        summary.append({
            "category": cat_name,
            "measure": measure,
            "latest":  last_val,
            "average": avg_val,
            "min":     min_val,
            "max":     max_val,
            "unit":    unit_val,
        })

    return summary


def get_date_range(crop: str, soil: str):
    """
    Build Timeline Focus dropdown options grouped by calendar year of actual samples.
    """
    df_raw = _read_custom_csv(DATA_PATH)
    df_raw['CreatedDate']   = pd.to_datetime(df_raw['CreatedDate'],   dayfirst=True, errors='coerce')
    df_raw['CropStartDate'] = pd.to_datetime(df_raw['CropStartDate'], dayfirst=True, errors='coerce')
    df_raw['CropEndDate']   = pd.to_datetime(df_raw['CropEndDate'],   dayfirst=True, errors='coerce')
    df_raw = df_raw.rename(columns={'Plant/Crop': 'Crop'})

    sub = df_raw.copy()
    if crop and crop != 'All Crops':
        sub = sub[sub['Crop'] == crop]
    if soil and soil != 'All Soils':
        sub = sub[sub['SoilType'] == soil]
        
    sub = sub.dropna(subset=['CreatedDate'])

    if sub.empty:
        return {"windows": []}

    sub = sub.copy()
    sub['sample_year'] = sub['CreatedDate'].dt.year

    yearly = (
        sub.groupby('sample_year')['CreatedDate']
        .agg(first_sample='min', last_sample='max')
        .reset_index()
        .sort_values('first_sample')
    )

    out = []
    for _, row in yearly.iterrows():
        fs = row['first_sample']
        ls = row['last_sample']
        label = f"{fs.strftime('%b %Y')} - {ls.strftime('%b %Y')}"
        out.append({
            "label":        label,
            "first_sample": fs.strftime('%Y-%m-%d %H:%M:%S'),
            "last_sample":  ls.strftime('%Y-%m-%d %H:%M:%S'),
            "year":         int(row['sample_year']),
        })

    return {"windows": out}


def get_soil_trajectory(crop: str, soil: str):
    """
    Returns time-series data filtered to SOIL-RELATED categories only.
    Groups by (CreatedDate, BatchId, Category) and returns per-measure values
    so the frontend can draw a trajectory plot coloured by measure.
    """
    df = get_data()
    sub = df.copy()
    if crop and crop != 'All Crops':
        sub = sub[sub['Crop'] == crop]
    if soil and soil != 'All Soils':
        sub = sub[sub['SoilType'] == soil]
        
    sub = sub[sub['Category'].isin(SOIL_CATEGORIES)]

    if sub.empty:
        return {"data": [], "soil_categories_used": []}

    # Which soil categories are actually present in this subset
    cats_used = sorted(sub['Category'].dropna().unique().tolist())

    pivot = sub.pivot_table(
        index=['CreatedDate', 'BatchId', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'],
        columns='Measure',
        values='ValueS',
        aggfunc='first'
    ).reset_index()

    pivot = pivot.sort_values(['CreatedDate', 'BatchId'])

    pivot['date'] = pivot.apply(
        lambda row: f"{row['CreatedDate'].strftime('%Y-%m-%d %H:%M:%S')} (Batch {row['BatchId']})",
        axis=1
    )
    
    pivot = pivot.drop(columns=['CreatedDate', 'BatchId'])
    pivot = pivot.replace({np.nan: None, 'Unknown': None, -999.0: None, -999: None})

    return {
        "data": pivot.to_dict(orient='records'),
        "soil_categories_used": cats_used,
    }


def get_plant_trajectory(crop: str, soil: str):
    """
    Returns time-series data filtered to PLANT-RELATED categories only.
    """
    df = get_data()
    sub = df.copy()
    if crop and crop != 'All Crops':
        sub = sub[sub['Crop'] == crop]
    if soil and soil != 'All Soils':
        sub = sub[sub['SoilType'] == soil]
        
    sub = sub[sub['Category'].isin(PLANT_CATEGORIES)]

    if sub.empty:
        return {"data": [], "plant_categories_used": []}

    cats_used = sorted(sub['Category'].dropna().unique().tolist())

    pivot = sub.pivot_table(
        index=['CreatedDate', 'BatchId', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'],
        columns='Measure',
        values='ValueS',
        aggfunc='first'
    ).reset_index()

    pivot = pivot.sort_values(['CreatedDate', 'BatchId'])

    pivot['date'] = pivot.apply(
        lambda row: f"{row['CreatedDate'].strftime('%Y-%m-%d %H:%M:%S')} (Batch {row['BatchId']})",
        axis=1
    )
    
    pivot = pivot.drop(columns=['CreatedDate', 'BatchId'])
    pivot = pivot.replace({np.nan: None, 'Unknown': None, -999.0: None, -999: None})

    return {
        "data": pivot.to_dict(orient='records'),
        "plant_categories_used": cats_used,
    }