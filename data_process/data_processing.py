import pandas as pd
import os

# Path to the directory containing your CSV files
directory = 'C:/Users/Lukas Svendsen/Desktop/visualisering/data'

# Initialize an empty DataFrame with the same columns as your CSV files
df = pd.DataFrame(columns=['Location', 'Species'])

# Get a list of all CSV files in the directory
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

# Total number of files for progress tracking
total_files = len(csv_files)

# Loop through each file and append its contents to the DataFrame
for i, filename in enumerate(csv_files):
    file_path = os.path.join(directory, filename)
    temp_df = pd.read_csv(file_path, delimiter=';')  # Specify the delimiter

    # Extract additional information from file name
    parts = filename.split('_')
    location = parts[1]
    species = parts[2].split('.')[0]  # Remove the .csv part

    # Add new information as columns
    temp_df['Location'] = location
    temp_df['Species'] = species

    df = df.append(temp_df, ignore_index=True)

    # Print the progress
    print(f'Processed {i + 1}/{total_files} files: {filename}')

# Remove (1), (2), etc., from all cells in the 'Species' column
df['Species'] = df['Species'].str.replace(r"\(\d+\)", "", regex=True)

# Now df contains all your data
df.rename(columns={'årstal':'Year', 'antal':'Count'}, inplace=True)

df['Year'] = df['Year'].astype(int)
df['Count'] = df['Count'].astype(int)

df.to_csv("data.csv", index=False)