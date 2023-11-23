import requests
import csv
import os
import time
from tqdm import tqdm

# Base path for the AQI Data
base_path = "AQI Data/Criteria Gases"

# Parameter codes for Criteria Gases
param_codes = {
    "PM2.5 FRM_FEM Mass Data": "88101",	
    "PM2.5 non_FRM_FEM Mass Data": "88502",	
    "PM10 Mass Data": "81102",	
    "PMc Mass Data":  "86101",
}

# County codes in New Mexico
counties = {
    "001": "Bernalillo",
    "003": "Catron",
    "005": "Chaves",	
    "006": "Cibola",	
    "007": "Colfax",	
    "009": "Curry",	
    "011": "De Baca",
    "013": "Dona Ana",
    "015": "Eddy",	
    "017": "Grant",	
    "019": "Guadalupe",	
    "021": "Harding",
    "023": "Hidalgo",	
    "025": "Lea",
    "027": "Lincoln",	
    "028": "Los Alamos",	
    "029": "Luna",	
    "031": "McKinley",	
    "033": "Mora",	
    "035": "Otero",	
    "037": "Quay",	
    "039": "Rio Arriba",	
    "041": "Roosevelt",	
    "043": "Sandoval",	
    "045": "San Juan",
}

# AQS API details
aqs_base_url = "https://aqs.epa.gov/data/api"
email = "simon.rhys.ballard@gmail.com"  # Replace with your AQS API credentials
key = "boleosprey46"   # Replace with your AQS API credentials

# Function to create folders
def create_folders():
    for gas, _ in param_codes.items():
        path = os.path.join(base_path, gas)
        for _, county_name in counties.items():
            county_path = os.path.join(path, county_name)
            os.makedirs(county_path, exist_ok=True)

# Function to fetch data from AQS API
def fetch_aqs_data(email, key, param_code, bdate, edate, state_code, county_code, year):
    url = f"{aqs_base_url}/dailyData/byCounty?email={email}&key={key}&param={param_code}&bdate={bdate}&edate={edate}&state={state_code}&county={county_code}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'Data' in data:
                return data['Data']
            else:
                print(f"No data found for {param_code}, {county_code}, {year}. Response: {data}")
                return []
        else:
            print(f"Error fetching data: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []


# Function to save data to CSV
def save_to_csv(data, file_path):
    if not data:
        print(f"No data available to write to {file_path}")
        return

    with open(file_path, 'w', newline='') as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Main data retrieval and saving process
def main():
    create_folders()
    total_iterations = len(param_codes) * len(counties) * len(range(2010, 2023))

    with tqdm(total=total_iterations, desc="Processing Data") as pbar:
        for gas, param_code in param_codes.items():
            for county_code, county_name in counties.items():
                for year in range(2010, 2023):
                    bdate = f"{year}0101"
                    edate = f"{year}1231"
                    data = fetch_aqs_data(email, key, param_code, bdate, edate, "35", county_code, year)
                    if data:
                        file_path = os.path.join(base_path, gas, county_name, f"{county_name}_{year}.csv")
                        save_to_csv(data, file_path)
                    
                    pbar.update(1)
                    time.sleep(5)  # Adhering to the API's usage policy

if __name__ == "__main__":
    main()