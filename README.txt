===========================================================================
                        EPA AQI Data Fetching Script
===========================================================================

OVERVIEW
--------
This Python script fetches air quality data from the EPA Air Quality Index (AQI) API. 
It allows users to select specific parameter classes, view available parameters, 
and download data for specified years and counties.

REQUIREMENTS
------------
- Python 3.x
- 'requests' library (install via 'pip install requests')
- Internet access to reach the EPA AQI API

FEATURES
--------
- Fetches data for multiple parameter classes from the EPA AQI API.
- User selection of parameter classes and viewing of available parameters.
- Adheres to EPA AQI API's rate limits (max 10 requests/minute, 5-sec pause between requests).
- Organizes data into directories by parameter class, county, and parameter.
- Progress bar displayed during data download.

USAGE
-----
1. Set up your environment:
   Ensure Python 3.x is installed and 'requests' library is available.

2. Run the script:
   Navigate to the script's directory in terminal/command prompt and run:
   > python combined_script.py

3. Enter API credentials and preferences:
   Input your EPA AQI API email, API key, start year, end year, and parameter classes.

4. Review and confirm the download:
   The script displays parameters under selected classes for confirmation.

5. Data organization:
   Data is saved in 'AQI Data' directory, sorted by parameter class, county, and parameter.

IMPORTANT NOTES
---------------
- Correctly input EPA AQI API key and email. The script exits if credentials are invalid.
- The script manages request frequency and data query size to comply with API rate limits.
- Large data requests may take significant time due to API limits and data processing.

===========================================================================
