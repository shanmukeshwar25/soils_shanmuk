import pandas as pd
import io
import re

with open('analysis_data_09-04-2026_2(in).csv', 'r', encoding='utf-8') as f:
    text = f.read()

if text.startswith('\ufeff'):
    text = text[1:]

text = re.sub(r'(?m)^\"|\"$', '', text)
text = text.replace('""', '"')

df = pd.read_csv(io.StringIO(text))
print("Columns:", df.columns.tolist())

if 'Category' in df.columns:
    cats = df['Category'].dropna().unique().tolist()
    print("Category values:", cats)
    print("Total category values:", len(cats))
    # Show value counts
    print("\nCategory value counts:")
    print(df['Category'].value_counts().head(30))
else:
    print("NO Category column found!")
    # Check for similar columns
    for c in df.columns:
        if 'cat' in c.lower():
            print(f"Possible match: {c}")
