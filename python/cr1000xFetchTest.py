import pandas as pd
import requests
import plotly.express as px


def cr1000x_plot(df :pd.DataFrame, varname :str) :
    
    # Plot one variable 
    fig = px.scatter(df, x='time', y=varname)
    fig.data[0].update(mode='markers+lines')
    fig.show()

def cr1000x_to_dataframe(data :dict) -> pd.DataFrame :

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


def cr1000x_fetch_json(table_name :str, logger_ip :str, *args, **kwargs) -> dict:
    """ Fetch all data from table_name, according to mode, p1, and p2 parameter.

        Default: mode = 'Backfill', p1 = 300 sec

        Return it as a Python dict.

        Campbell CR1000x Web Server API commands documented here:
        https://help.campbellsci.com/crbasic/cr1000x/Content/Info/webserverapicommands1.htm
        
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
    p1 = 30      # Most recent 30 records
    p2 = None 

    # mode = 'Backfill'
    # p1 = 10   # Last 10 seconds of recorded data
    # p2 = 0

    # Retrieve using default mode='Backfill', p1=300 sec
    # data = fetch_cr1000x_json(table_name, logger_ip, mode)

    # Retrieve from CR1000x with optional named keyword arguments
    data = cr1000x_fetch_json(table_name, logger_ip, mode=mode, p1=p1, p2=p2)

    # Process data into dataframe, then plot it.
    if data:
        print("JSON data retrieved successfully")

        # extract data to Pandas dataframe
        df = cr1000x_to_dataframe(data)

        # Display DataFrame
        print(df)

        # plot one variable vs. time
        cr1000x_plot(df, 'ECO_Beta700')

# Example usage
if __name__ == "__main__":
    main()