import sqlite3
from tabulate import tabulate

# Connect to the SQLite database
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# Read and execute SQL queries from "query.sql"
with open('query.sql', 'r') as query_file:
    sql_queries = query_file.read()

    # Split multiple queries (if any) by semicolon and execute them one by one
    for query in sql_queries.split(';'):
        query = query.strip()
        if query:  # Check if the query is not empty
            cursor.execute(query)
            conn.commit()

            # If the query is a SELECT query, format and print the results as a table
            if query.lower().startswith('select'):
                results = cursor.fetchall()
                if results:
                    # Get column names
                    column_names = [description[0] for description in cursor.description]

                    # Create a list of lists to include the column names and the data
                    table_data = [column_names] + [list(row) for row in results]

                    # Print the table using tabulate
                    table = tabulate(table_data, headers="firstrow", tablefmt="pretty")
                    print(table)
                else:
                    print("No results found.")

# Close the database connection
conn.close()
