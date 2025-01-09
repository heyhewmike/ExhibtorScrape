# NRF-ExhibitorScrape
## Requirements
1. selenium
2. pandas
3. openpyxl
4. Firefox - Windows installer https://download.mozilla.org/?product=firefox-stub&os=win&lang=en-US

### This was intended for the National Retail Federation for the 2025 Jan site

## How to run
1. ensure you have installed all above Requirement packages
2. ensure you address all errors that appear when attempting to run such as missing packages

1. open a PS or terminal in the folder/directory with nrf.py & geckodriver
2. based on your OS run the python script
    Example:
        Linux: 
            1. dos2unix nrf.py
            2. chmod +x nrf.py
            3. python3 ./nrf.py
        Windows:
            1. python.exe nrf.py
3. You will see NO output in your terminal/PS


## How to see results
1. Open the folder named "nrf_" followed by the the YearMonthDate-HourMinute of the run. You can find this folder made in the same folder/directory the script was run from.
2. You will see a folder named "NRF_Results.log" where error and status logging happens. Documentation of all Exhibitors are found here also.
    All Exhibitor info can be found between "*&#" and "#&*"