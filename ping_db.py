import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
# (Useful if running locally, GitHub Actions will use its own secrets)
load_dotenv()

def ping_database():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL is not set. Cannot ping database.")
        return

    # Skip pinging if it's a local SQLite database
    if db_url.startswith('sqlite'):
        print("Using SQLite. No need to ping for keep-alive.")
        return

    try:
        print("Attempting to ping Supabase database...")
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Execute a simple, lightweight query
        cur.execute('SELECT 1;')
        
        # Fetch the result
        result = cur.fetchone()
        
        if result and result[0] == 1:
            print("Database ping successful! Supabase is active.")
        else:
            print(f"Unexpected result: {result}")
        
        # Close connection
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error pinging database: {e}")

if __name__ == '__main__':
    ping_database()
