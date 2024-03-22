import pandas as pd
import requests
import json

def cr1000x_to_dataframe(data) :

    # Extract field names
    fields = [field['name'] for field in data['head']['fields']]

    # Process data
    rows = []
    for entry in data['data']:
        row = dict(zip(fields, entry['vals']))
        row['time'] = entry['time']
        rows.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Convert time column to datetime
    df['time'] = pd.to_datetime(df['time'])

    return df


def cr1000x_fetch_json(table_name, logger_ip, *args, **kwargs):
    """ Fetch all data from table_name, according to mode, p1, and p2 parameter.

        Default: mode = 'Backfill', p1 = 300 sec

        Return it as a Python dict.
        
    """
        # get optional arguments
    # Default mode is 'Backfill' with last 5 min of data (300 s)
    mode = kwargs.get('mode', 'Backfill')
    p1 = kwargs.get('p1', 300)
    p2 = kwargs.get('p2', None)

    # Define API endpoint URL
    endpoint = f"http://{logger_ip}/"
   
    # Basic dataquery returning json 
    params = {
        "command" : "dataquery",
        "Uri": f"dl:{table_name}",
        "format" : "json",
        "mode" : mode,
        "p1" : p1,
    }

    if not (p2 is None) :
        params['p2'] = p2
    
    # Try http dataquery to the CR1000x
    try:
        # Send GET request to fetch data
        response = requests.get(endpoint, params=params)

        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error fetching data. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None

def main() :

    # Static ip of CR1000x
    logger_ip = "192.168.50.91"

    # Which table to retrieve
    table_name = "EcoTriplet"

    # Select desired mode and relate arguments p1, p2
    mode = 'most-recent'
    p1 = 3      # Most recent 3 records
    p2 = None 

    # mode = 'Backfill'
    # p1 = 10   # Last 10 seconds of recorded data
    # p2 = 0

    # Retrieve using default mode='Backfill', p1=300 sec
    # data = fetch_cr1000x_json(table_name, logger_ip, mode)

    # Retrieve from CR1000x with optional named keyword arguments
    data = cr1000x_fetch_json(table_name, logger_ip, mode=mode, p1=p1, p2=p2)
    if data:
        print("JSON data retrieved successfully")

        # extract data to Pandas dataframe
        df = cr1000x_to_dataframe(data)

        # Display DataFrame
        print(df)

# Example usage
if __name__ == "__main__":
    main()