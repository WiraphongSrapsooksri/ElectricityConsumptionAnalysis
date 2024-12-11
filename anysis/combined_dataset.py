import os
import pandas as pd

# Path to the preprocessingdata folder
preprocessed_data_dir = "../preprocessingdata"

# List to store DataFrames
data_frames = []

# Loop through each year folder
for year in os.listdir(preprocessed_data_dir):
    year_path = os.path.join(preprocessed_data_dir, year)
    if os.path.isdir(year_path):  # Check if it's a folder
        for file in os.listdir(year_path):
            if file.endswith(".csv"):  # Process only CSV files
                file_path = os.path.join(year_path, file)
                try:
                    # Read each CSV file
                    df = pd.read_csv(file_path)

                    # Add Year and Month columns for reference
                    df['Year'] = year
                    df['Month'] = file[:2]  # Extract the first two characters as month (e.g., "01", "02")

                    # Append the DataFrame to the list
                    data_frames.append(df)
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

# Combine all DataFrames into one
if data_frames:
    all_data = pd.concat(data_frames, ignore_index=True)
    print("Dataset created successfully!")
    
    # Save as CSV for future use
    all_data.to_csv("combined_dataset.csv", index=False, encoding='utf-8-sig')
    print("Combined dataset saved as 'combined_dataset.csv'")

else:
    print("No data found in preprocessingdata folder.")
