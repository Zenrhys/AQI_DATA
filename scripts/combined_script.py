import requests
import csv
import os
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to fetch parameter codes for a specific class
def fetch_parameter_codes_for_class(email, key, param_class):
    url = f"https://aqs.epa.gov/data/api/list/parametersByClass?email={email}&key={key}&pc={param_class}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['Data']
            return {item['value_represented']: item['code'] for item in data}
        else:
            print(f"Error: HTTP {response.status_code}. Please check your API key and email.")
            return None  # Return None to indicate an error
    except Exception as e:
        print(f"Exception occurred while fetching parameters for class {param_class}: {e}")
        return None  # Return None to indicate an error

def fetch_parameters_in_parallel(email, key, classes):
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_class = {executor.submit(fetch_parameter_codes_for_class, email, key, param_class): param_class for param_class in classes}
        for future in as_completed(future_to_class):
            param_class = future_to_class[future]
            try:
                result = future.result()
                if result is not None:
                    results[param_class] = result
                time.sleep(5)  # Adhering to rate limit of 5 seconds between requests
            except Exception as exc:
                print(f'{param_class} generated an exception: {exc}')
    return results

# Function to create folders
def create_folders(base_path, counties, param_codes):
    for param_class, codes in param_codes.items():
        for county_name in counties.values():
            for param_name in codes.keys():
                param_folder_path = os.path.join(base_path, param_class, county_name, param_name)
                os.makedirs(param_folder_path, exist_ok=True)


# Function to fetch data from AQS API
def fetch_aqs_data(email, key, param_code, bdate, edate, state_code, county_code):
    url = f"https://aqs.epa.gov/data/api/dailyData/byCounty?email={email}&key={key}&param={param_code}&bdate={bdate}&edate={edate}&state={state_code}&county={county_code}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'Data' in data:
                return data['Data']
    except Exception as e:
        print(f"Error fetching data: {e}")
    return []

# Function to save data to CSV
def save_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Function to get user class selections
def get_user_class_selections():
    param_classes = {
        "CORE_HAPS": "Urban Air Toxic Pollutants",
        "CRITERIA": "Criteria Pollutants",
        "PAH": "Polycyclic Aromatic Hydrocarbons",
        "APP_A_PARAMETERS": "Parameters subject to the 40 CFR Appendix A Regulations",
        "AQI POLLUTANTS": "Pollutants that have an AQI Defined",
        "CSN CARBON": "Chemical Speciation Network Organic and Elemental Carbon",
        "CSN IONS": "Ions measured by the Chemical Speciation Network program",
        "IMPROVE_SPECIATION": "PM2.5 Speciated Parameters Measured at IMPROVE sites",
        "NATTS CORE HAPS": "The core list of toxics of interest to the NATTS program.",
        "PAMS_VOC": "Volatile Organic Compound subset of the PAMS Parameters",
        "SPECIATION": "PM2.5 Speciated Parameters",
        "SPECIATION CATION/ANION": "PM2.5 Speciation Cation/Anion Parameters",
        "UATMP CARBONYL": "Urban Air Toxics Monitoring Program Carbonyls",
        "UATMP VOC": "Urban Air Toxics Monitoring Program VOCs",
        "VOC": "Volatile organic compounds",
        "HAPS": "Hazardous Air Pollutants",
    }
    
    print("Available Parameter Classes:")
    for code, name in param_classes.items():
        print(f"{code}: {name}")

    selections = input("Enter the class codes you want to download, separated by commas (e.g., VOC,HAPS): ")
    selected_codes = [code.strip() for code in selections.split(',')]
    return [code for code in selected_codes if code in param_classes]

# Function to display parameters for classes
def display_parameters_for_classes(param_codes):
    for param_class, codes in param_codes.items():
        print(f"\nParameters for class {param_class}:")
        for name, code in codes.items():
            print(f"  {name} ({code})")


# Main data retrieval and saving process
def main():
    email = input("Enter your AQS API email: ")
    key = input("Enter your AQS API key: ")
    start_year = int(input("Enter the start year (e.g., 2010): "))
    end_year = int(input("Enter the end year (e.g., 2023): "))
    state_code = "35"
    base_path = "AQI Data"
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

    selected_classes = get_user_class_selections()

    print("Fetching parameter data, please wait...")
    param_codes = fetch_parameters_in_parallel(email, key, selected_classes)
    if not param_codes:  # Check if param_codes is empty or None
        print("Terminating due to invalid API credentials or connection issue.")
        return  # Exit the script

    display_parameters_for_classes(param_codes)

    confirmation = input("Proceed with download? (yes/no): ")
    if confirmation.lower() != 'yes':
        print("Download cancelled.")
        return

    total_iterations = sum(len(counties) * len(codes) * (end_year - start_year + 1) for codes in param_codes.values())
    with tqdm(total=total_iterations, desc="Downloading and Saving Data") as pbar:
        for param_class, codes in param_codes.items():
            create_folders(base_path, counties, {param_class: codes})
            for county_code, county_name in counties.items():
                for param_name, param_code in codes.items():
                    for year in range(start_year, end_year + 1):
                        bdate = f"{year}0101"
                        edate = f"{year}1231"
                        data = fetch_aqs_data(email, key, param_code, bdate, edate, state_code, county_code)
                        if data:
                            file_path = os.path.join(base_path, param_class, county_name, param_name, f"{param_name}_{county_name}_{year}.csv")
                            save_to_csv(data, file_path)
                        pbar.update(1)


    param_codes = {}
    for param_class in selected_classes:
        param_codes[param_class] = fetch_parameter_codes_for_class(email, key, param_class)


    create_folders(base_path, counties, param_codes)
    
    for param_class, codes in param_codes.items():
        for param_name, param_code in codes.items():
            for county_code, county_name in counties.items():
                bdate = f"{start_year}0101"
                edate = f"{end_year}1231"
                data = fetch_aqs_data(email, key, param_code, bdate, edate, state_code, county_code)
                if data:
                    file_path = os.path.join(base_path, param_class, county_name, f"{param_name}_{county_name}_{start_year}-{end_year}.csv")
                    save_to_csv(data, file_path)
                    print(f"Data saved for {param_name} in {county_name}.")


if __name__ == "__main__":
    main()
