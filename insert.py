import pandas as pd
import mysql.connector

# Load the Excel file (Change the filename if needed)
file_path = "coffeeroom_remaining.xlsx"  # Replace with your actual file path
df = pd.read_excel(file_path)

# Add the outlet name as "Abc"
df["outlet_name"] = "Coffee Room, Baneshwor"

# Connect to MySQL
# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Info@silverline.com",  # Replace with your MySQL password
    database="thecorefood"   # Replace with your database name
)
cursor = conn.cursor()

# SQL query to insert data
insert_query = """
    INSERT INTO tblDailySales (date, sales, outlet_name)
    VALUES (%s, %s, %s)
"""

# Insert each row into the database
for _, row in df.iterrows():
    # Assuming "Total Sales" column in the Excel file
    cursor.execute(insert_query, (row["Date"], row["Total Sales"], row["outlet_name"]))

# Commit and close the connection
conn.commit()
cursor.close()
conn.close()

print("Data uploaded successfully!")
