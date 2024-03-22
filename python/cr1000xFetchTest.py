import requests

def fetch_cr1000x_json(table_name, logger_ip, *args, **kwargs):

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

# Example usage
if __name__ == "__main__":

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

    # Retrieve with optional named keyword arguments
    data = fetch_cr1000x_json(table_name, logger_ip, mode=mode, p1=p1)
    if data:
        print("Data retrieved successfully:", data)