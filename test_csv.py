import pandas as pd
import io

def clean_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Handle utf-8 BOM if present on first line
        if line.startswith('\ufeff'):
            line = line[1:]
            
        if line.startswith('"') and line.endswith('"'):
            # It's an improperly quoted line
            # strip leading/trailing quote
            line = line[1:-1]
            # un-escape double quotes
            line = line.replace('""', '"')
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines)

try:
    csv_data = clean_csv(r'D:\Soil_vis\analysis_data_09-04-2026_2(in).csv')
    df = pd.read_csv(io.StringIO(csv_data))
    print('Clean read success!')
    print('Columns:', df.columns.tolist())
    print('Rows:', len(df))
except Exception as e:
    print('Error:', e)
