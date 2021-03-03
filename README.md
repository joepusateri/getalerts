# getalerts
Retrieve a list of all alerts (optionally on a certain service) with all custom details

## Files
* getalerts.py - main script
* requirements.txt - the Python required libraries.  

## Running

Parameters:

* `-k / --pd-token` = PagerDuty API Key (required) - This can be an API token (global or user) - readonly is sufficient.
* `-s / --start-date` = start date in the format YYYMMDD (required)
* `-e / --end-date` = end date in the format YYYMMDD (required)
* `-f / --filename` = Output file name (required)
* `-v / --service` = service id to filter alerts on (optional)
* `-d / --debug` (optional) - include this to print debug messages

Example:
```
python3 getalerts.py -k 0123456789001234567890 -s 20210201 -e 20210228 -v P141515 -f february.csv
```