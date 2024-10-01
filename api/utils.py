import psycopg2
import pandas as pd

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
        SELECT client_id, supply_period, date_time, hour, wesm, kwh
        FROM load_profiles.client_load_profile
        WHERE client_id = ANY(%s)
        """
        
        # Fetch data from the database
        with conn.cursor() as cur:
            cur.execute(query, (client_ids,))
            rows = cur.fetchall()
        
        # Define the column names (ensure they match the database table structure)
        columns = ['client_id', 'supply_period', 'date_time', 'hour', 'wesm', 'kwh']
        
        # Convert to a pandas DataFrame
        data = pd.DataFrame(rows, columns=columns)
        return data
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
