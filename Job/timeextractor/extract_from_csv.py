import pandas as pd
from extractor import TimeExtractor

# Load CSV
df = pd.read_csv(r"C:\Users\victo\Desktop\CS\Job\timeextractor\Supabase_Snippet_Event_Management_Table.csv")

# Init extractor
extractor = TimeExtractor()

def extract_time(text):
    if pd.isna(text):
        return None
    result = extractor.extract(text)
    return [r.datetime.isoformat() for r in result if r.datetime]

df["extracted_times"] = df["description"].apply(extract_time)

df.to_csv("extracted_times_output.csv", index=False)
print("✅ Extraction complete.")
