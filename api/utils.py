import psycopg2
import pandas as pd
from pandas import DateOffset

def connect_database():
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gcb",
            user="postgres",
            password="123456",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def fetch_effective_rates(conn, client_ids):
    """
    Fetches data from the load_profiles.client_load_profile table based on client_ids.
    """
    try:
        # Build the SQL query
        query = """
        SELECT client_id, supply_period, date_time, hour, wesm, kw
        FROM load_profiles.client_load_profile
        WHERE client_id = ANY(%s)
        """
        
        # Fetch data from the database
        with conn.cursor() as cur:
            cur.execute(query, (client_ids,))
            rows = cur.fetchall()
        
        # Define the column names (ensure they match the database table structure)
        columns = ['client_id', 'supply_period', 'date_time', 'hour', 'wesm', 'kw']
        
        # Convert to a pandas DataFrame
        data = pd.DataFrame(rows, columns=columns)
        data['datetime'] = pd.to_datetime(data['date_time'])  # Ensure 'datetime' is in the correct format
        return data
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_supply_period(date):
    """
    Determines the supply period for the given date.
    """
    if date.day >= 26:
        period_start = date.replace(day=26)
        period_end = (period_start + DateOffset(months=1)).replace(day=25)
    else:
        period_end = date.replace(day=25)
        period_start = (period_end - DateOffset(months=1)).replace(day=26)
    return period_end.strftime('%b-%y'), period_end
