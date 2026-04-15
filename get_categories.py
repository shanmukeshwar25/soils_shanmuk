import sys
import os

# add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
import data_processing
import pandas as pd

df_raw = data_processing._read_custom_csv(data_processing.DATA_PATH)
categories = df_raw['Category'].dropna().unique().tolist()
print("Categories:", categories)

# Show a few examples of soil vs non-soil related categories
sample_measures = df_raw.groupby('Category')['Measure'].unique().apply(list).to_dict()
for cat in categories:
    print(f"\nCategory: {cat}")
    print(f"Measures: {sample_measures.get(cat, [])}")
