"""
Script to check the PostgreSQL schema directly.
"""

import psycopg2
import psycopg2.extras

# Connect to the database
conn_string = "postgresql://jira:jira@docker.lan:5432/postgres"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Query the table definition
cursor.execute("""
    SELECT column_name, data_type, udt_name
    FROM information_schema.columns
    WHERE table_name = 'job_descriptions';
""")

# Print the results
print("\nTable column definitions for job_descriptions:")
print("---------------------------------------------")
for row in cursor.fetchall():
    print(f"Column: {row['column_name']}, Type: {row['data_type']}, UDT: {row['udt_name']}")

# Close the connection
cursor.close()
conn.close()
