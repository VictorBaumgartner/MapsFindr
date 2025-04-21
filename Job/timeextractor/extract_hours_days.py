import re
import pandas as pd
from datetime import datetime

def extract_times_by_day(text):
    """
    Extracts times from a given text and associates them with specific days of the week.

    Args:
        text (str): The text to extract time information from.

    Returns:
        dict: A dictionary where keys are days of the week and values are lists of times.
    """

    days_of_week = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    daily_times = {}

    for day in days_of_week:
        daily_times[day] = []

    # Regex to find times, including ranges and specific times
    time_regex = r"(\d{1,2}[h:]\d{2}|\d{1,2}h?)\s*(?:à|-)?\s*(\d{1,2}[h:]\d{2}|\d{1,2}h?)?"

    for day in days_of_week:
        # Find times mentioned for each day
        matches = re.findall(rf"{day}\s*{time_regex}", text, re.IGNORECASE)
        for match in matches:
            time1 = match[0]
            time2 = match[1] if match[1] else ""  # Use empty string if no second time

            if time2:
                daily_times[day].append(f"{time1}-{time2}")  # Store time range
            else:
                daily_times[day].append(time1)  # Store single time


     #Find opening hours mentioned for "Du ... au ..." like "Du mardi au samedi, de 10h à 18h."
    matches = re.findall(rf"du\s*({days_of_week[0]}|{days_of_week[1]}|{days_of_week[2]}|{days_of_week[3]}|{days_of_week[4]}|{days_of_week[5]}|{days_of_week[6]})\s*au\s*({days_of_week[0]}|{days_of_week[1]}|{days_of_week[2]}|{days_of_week[3]}|{days_of_week[4]}|{days_of_week[5]}|{days_of_week[6]}),\s*de\s*(\d{{1,2}}[h:]\d{{2}}|\d{{1,2}}h?)\s*à\s*(\d{{1,2}}[h:]\d{{2}}|\d{{1,2}}h?)", text, re.IGNORECASE)
    if matches:
        start_day = matches[0][0].lower()
        end_day = matches[0][1].lower()
        start_time = matches[0][2]
        end_time = matches[0][3]

        start_index = days_of_week.index(start_day)
        end_index = days_of_week.index(end_day)

        for i in range(start_index, end_index + 1):
            day = days_of_week[i]
            daily_times[day].append(f"{start_time}-{end_time}")



    return daily_times


# Example usage with DataFrame
csv_file = r'C:\Users\victo\Desktop\CS\Job\timeextractor\Supabase_Snippet_Event_Management_Table.csv'
df = pd.read_csv(csv_file)

# Assuming the text is in the second column (index 1)
df['daily_times'] = df.iloc[:, 1].apply(extract_times_by_day)

# Function to format the output as a string
def format_times(daily_times):
    output = ""
    for day, times in daily_times.items():
        if times:
            output += f"{day}: {', '.join(times)}\n"
    return output

# Apply the function to create a formatted string
df['formatted_times'] = df['daily_times'].apply(format_times)

# Filter rows where there are any times
df_filtered = df[df['formatted_times'] != ""]  # Keep rows where formatted_times is not empty

# Select only the id and the formatted_times columns
df_output = df_filtered[['id', 'formatted_times']]

# Export to a CSV file
output_csv_file = r'C:\Users\victo\Desktop\CS\Job\timeextractor\extracted_times_formatted.csv'
df_output.to_csv(output_csv_file, index=False)

print(f"Extracted and formatted times exported to {output_csv_file}")
