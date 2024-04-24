import json
import pandas as pd
import requests
import plotly.express as px
from pathlib import Path
from dataclasses import dataclass

@dataclass
class cr1000x:
    
    """Class for cr1000x"""
    logger_ip : str

    def plot(self, df :pd.DataFrame, varname :str) :
    
        # Plot one variable 
        fig = px.scatter(df, x='time', y=varname)
        fig.data[0].update(mode='markers+lines')
        fig.show()

    def to_dataframe(self, data :dict) -> pd.DataFrame :

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


    def fetch(self, table_name :str, *args, **kwargs) -> dict:
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
        endpoint = f"http://{self.logger_ip}/"
    
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
            print(f"Unable to fetch data from logger {self.logger_ip}:", e)
            return None

    def read_CSIJSON(self, file_path :str) -> dict:
        """ Read data from CSIJSON file retrieved from a Campbell CR1000x logger.

            The JSON schema for this file is the same as JSON retrieve from the
            logger via the HTTP API using the fetch() method above.
        """

        # Open and load local JSON file

        try :
            with open(file_path) as json_file :
                data = json.load(json_file)
                return data
        except OSError as e :
            print(f'Unable to open local JSON file: {e}')
            # print(f'No such file or directory: {file_name}')

def main() :

    # Static ip of CR1000x
    logger_ip = "192.168.50.91"
    # logger_ip = "10.96.211.159"

    # Which table to retrieve
    table_name = "EcoTriplet"
    # table_name = "SeapHOx"

    # Which sensor to view
    sensor_name = "ECO_Beta700"
    # sensor_name = "SPHOX_T"

    # Create datalogger object
    datalogger = cr1000x(logger_ip)           

    # Example 1: Retrieve using default mode='Backfill', p1=300 sec
    data = datalogger.fetch(table_name, p1=300)

    # Select desired mode and relate argume, nts p1, p2
    # mode = 'most-recent'
    # p1 = 30      # Most recent 30 records
    # p2 = None 

    # mode = 'Backfill'
    # p1 = 10   # Last 10 seconds of recorded data
    # p2 = 0

    # Retrieve from CR1000x with optional named keyword arguments
    # data = datalogger.fetch(table_name, mode=mode, p1=p1, p2=p2)

    # Process data into dataframe, then plot it.
    if data:
        print(f"JSON data retrieved successfull from {logger_ip}")

        # extract data to Pandas dataframe
        df = datalogger.to_dataframe(data)

        # Display DataFrame
        print(df.tail())

        # plot one variable vs. time
        datalogger.plot(df, sensor_name)

    # Example 2: Read data from a file already retrieved from the logger
    # Note that the table name is implicit in the file_name
    # ToDo : method to retrieve file(s) from the logger.

    file_name = Path('/Volumes/[C] Windows 10/Campbellsci/PC400/EcoTriplet_94.dat')
    data = datalogger.read_CSIJSON(file_name)    
    if data:
        print(f"JSON data retrieved successfully from {file_name}")

        # extract data to Pandas dataframe
        df = datalogger.to_dataframe(data)

        # Display DataFrame
        print(df.tail())

        # plot one variable vs. time
        datalogger.plot(df, sensor_name) 

# Example usage
if __name__ == "__main__":
    main()