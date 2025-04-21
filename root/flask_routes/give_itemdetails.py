# from flask import Flask, jsonify, request, Blueprint

# import mysql.connector

# from flask_cors import cross_origin

# import os

# from dotenv import load_dotenv

# load_dotenv()

# app_file29 = Blueprint('app_file29', __name__)
# from root.auth.check import token_auth
# import pytz

# import re

# from datetime import datetime, timedelta

# @app_file29.route('/give_itemdetails', methods = ['POST'])

# @cross_origin()
# def give_itemdetails():
#     try:
#         mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         json = request.get_json()
#         if "token" not in json  or not any([json["token"]])  or json["token"]=="":
#             data = {"error":"No token provided."}
#             return data,400
#         token = json["token"]
#         if "outlet" not in json  or not any([json["outlet"]])  or json["outlet"]=="":
#             data = {"error":"No outlet provided."}
#             return data,400
#         outlet = json["outlet"]
#         if not token_auth(token):
#             data = {"error":"Invalid token."}
#             return data,400
#         if "name" not in json  or not any([json["name"]])  or json["name"]=="":
#             data = {"error":"No name provided."}
#             return data,400
#         # name = json["name"]
#         if not token_auth(token):
#             data = {"error":"Invalid token."}
#             return data,400
#         item_name = json.get('name', None)

#         group = json.get('description', None)

#         totals_sql = """select sum(a.Total) as Total_Revenue, sum(a.count) as Total_Count from tblorder_detailshistory a, tblorderhistory b where a.order_ID = b.idtblorderHistory and a.ItemName = %s and b.Outlet_Name=%s and b.bill_no != '';"""

#         cursor.execute(totals_sql, (item_name, outlet,))

#         totals_result = cursor.fetchone()

#         # Extract total and count into variables
#         if totals_result:
#             total_revenue, total_count = totals_result
#             # print(f"Total Revenue: {total_revenue}, Total Count: {total_count}")
#         else:
#             total_revenue, total_count = 0.0, 0.0  # Default values if no data is returned
#             # print("No data found.")

#         # Query to calculate the rank of the item within the same description
#         rank_sql = """
#         SELECT a.ItemName, 
#             RANK() OVER (ORDER BY SUM(a.Total) DESC) AS Rank 
#         FROM tblorder_detailshistory a, tblorderhistory b 
#         WHERE a.order_ID = b.idtblorderHistory 
#         AND a.Description = %s 
#         AND b.Outlet_Name = %s AND b.bill_no != ''
#         GROUP BY a.ItemName
#         """
#         cursor.execute(rank_sql, (group, outlet,))
#         rank_results = cursor.fetchall()


#         columns = [col[0] for col in cursor.description]

#         rank_results_responseJson = [dict(zip(columns, rows)) for rows in rank_results]
#         # Find the rank of the specific item
#         item_rank = None
#         for row in rank_results:
#             if row[0] == item_name:
#                 item_rank = row[1]
#                 break


#         # Calculate date range for the past month, starting on the same weekday
#         today = datetime.now()
#         weekday = today.weekday()  # 0=Monday, 6=Sunday
#         last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

#         # Find the first occurrence of the same weekday in the previous month
#         start_date = last_month + timedelta(days=(weekday - last_month.weekday()) % 7)

#         start_date_str = start_date.strftime("%Y-%m-%d")
#         today_date_str = today.strftime("%Y-%m-%d")
#         # print(f"start_date {start_date}")
#         # Prepare the 7-day interval query
#         interval_query = """
#         SELECT 
#             DATE(MIN(b.Date)) AS Start_Date,
#             COUNT(a.count) AS Total_Count
#         FROM tblorder_detailshistory a
#         INNER JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
#         WHERE a.ItemName = %s 
#         AND b.Outlet_Name = %s
#         AND b.Date BETWEEN %s AND %s
#         AND b.bill_no != ''
#         GROUP BY FLOOR(DATEDIFF(b.Date, %s) / 7)
#         ORDER BY Start_Date ASC;
#         """
        
#         # Execute the interval query
#         cursor.execute(interval_query, (item_name, outlet, start_date_str, today_date_str, start_date_str))
#         interval_results = cursor.fetchall()
#         # print(f"interval_results {interval_results}")

#         # Process results
#         interval_data = []

#         # Generate the expected 7-day intervals from start_date to today
#         current_start_date = start_date
#         intervals = []
#         i = 1
#         while current_start_date <= today:
#             current_end_date = current_start_date + timedelta(days=6)
#             intervals.append({
#                 "start_date": current_start_date,
#                 "end_date": min(current_end_date, today),  # Ensure end_date doesn't go beyond today
#                 "week": i,
#                 "total_count": 0  # Default to 0, will update later if data exists
#             })
#             current_start_date += timedelta(days=7)
#             i += 1
#         # print(intervals)
#         # Map query results for faster lookup
#         # Map query results for faster lookup (convert keys to strings)
#         query_results = {row[0].strftime("%Y-%m-%d"): row[1] for row in interval_results}  # {start_date_str: total_count}

#         # print(query_results)
#         # Update intervals with query results
#         for interval in intervals:
#             start_date_str = interval["start_date"].strftime("%Y-%m-%d")
#             interval["total_count"] = query_results.get(start_date_str, 0)
#             interval["start_date"] = start_date_str  # Convert to string for JSON response
#             interval["end_date"] = interval["end_date"].strftime("%Y-%m-%d")

#         # Assign to interval_data
#         interval_data = intervals


#         # Define all months
#         all_months = [
#             "January", "February", "March", "April", "May", "June",
#             "July", "August", "September", "October", "November", "December"
#         ]

#         # Calculate the start and end dates for one year range
#         yearly_end_date = datetime.now().date()  # Today's date
#         yearly_start_date = yearly_end_date - timedelta(days=365)  # Date one year before



#         # Generate a list of months in the desired range
#         def get_month_year_range(yearly_start_date, yearly_end_date):
#             months = []
#             current_date = yearly_start_date.replace(day=1)  # Start from the first day of the month
#             while current_date <= yearly_end_date:
#                 months.append(f"{all_months[current_date.month - 1]} {current_date.year}")
#                 # Move to the first day of the next month
#                 if current_date.month == 12:  # December
#                     current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
#                 else:
#                     current_date = current_date.replace(month=current_date.month + 1, day=1)
#             return months

#         # Get the range of months
#         month_year_range = get_month_year_range(yearly_start_date, yearly_end_date)

#         # Initialize dictionaries for sales and purchases with the correct range
#         sales_data = {
#             month_year: {"TotalSales": "0.0", "monthName": month_year, "TotalCount": "0"}
#             for month_year in month_year_range
#         }

#         yearly_start_date_str = yearly_start_date.strftime("%Y-%m-%d")
#         yearly_end_date_str = yearly_end_date.strftime("%Y-%m-%d")
#         # Example SQL queries to fetch data (replace with actual database execution)
#         sql_query_sales = """
#             SELECT 
#                 YEAR(b.Date) AS year,
#                 MONTH(b.Date) AS month, 
#                 SUM(a.Total) AS totalSales, 
#                 SUM(a.count) AS totalCount 

#             FROM tblorder_detailshistory a ,tblorderhistory b
#             WHERE a.order_ID = b.idtblorderHistory and a.ItemName = %s and b.Date BETWEEN %s AND %s and b.Outlet_Name = %s and b.bill_no != ''
#             GROUP BY YEAR(Date), MONTH(Date)
#         """
#         cursor.execute(sql_query_sales, (item_name, yearly_start_date_str, yearly_end_date_str, outlet,))
#         sales_results = cursor.fetchall()
#         print(yearly_start_date)
#         print(yearly_end_date)
#         print(sales_results)
#         # Populate sales data
#         for year, month, totalSales, totalCount in sales_results:
#             month_name = f"{all_months[month - 1]} {year}"  # Combine month and year
#             if month_name in sales_data:
#                 sales_data[month_name] = {"TotalSales": str(totalSales), "monthName": month_name, "TotalCount": str(totalCount)}

#         # Convert dictionaries to lists
#         sales_json = list(sales_data.values())

#         response_data = {
#             "Total_Revenue" : total_revenue,
#             "Total_Count" : total_count,
#             "Group_Ranking" : item_rank,
#             "Last_Monthly" : interval_data,
#             "Group_AllItem_Ranks": rank_results_responseJson,
#             "Yearly_sales_json": sales_json

#         }

#         return response_data, 200
    
#     except mysql.connector.Error as db_error:
#         return jsonify({"error": f"Database error: {str(db_error)}"}), 500
#     except Exception as error:
#         return jsonify({"error": f"Internal server error: {str(error)}"}), 500
#     finally:
#         # Ensure the cursor and connection are closed
#         if cursor:
#             cursor.close()
#         if mydb:
#             mydb.close()    


from flask import Flask, jsonify, request, Blueprint

import mysql.connector

from flask_cors import cross_origin

import os

from dotenv import load_dotenv

load_dotenv()

app_file29 = Blueprint('app_file29', __name__)
from root.auth.check import token_auth
import pytz

import re

from datetime import datetime, timedelta

@app_file29.route('/give_itemdetails', methods = ['POST'])

@cross_origin()
def give_itemdetails():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = {"error":"No token provided."}
            return data,400
        token = json["token"]
        if "outlet" not in json  or not any([json["outlet"]])  or json["outlet"]=="":
            data = {"error":"No outlet provided."}
            return data,400
        outlet = json["outlet"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            return data,400
        if "name" not in json  or not any([json["name"]])  or json["name"]=="":
            data = {"error":"No name provided."}
            return data,400
        # name = json["name"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            return data,400
        item_name = json.get('name', None)

        group = json.get('description', None)

        totals_sql = """select sum(a.Total) as Total_Revenue, sum(a.count) as Total_Count from tblorder_detailshistory a, tblorderhistory b where a.order_ID = b.idtblorderHistory and a.ItemName = %s and b.Outlet_Name=%s and b.bill_no != '';"""

        cursor.execute(totals_sql, (item_name, outlet,))

        totals_result = cursor.fetchone()

        # Extract total and count into variables
        if totals_result:
            total_revenue, total_count = totals_result
        else:
            total_revenue, total_count = 0.0, 0.0  # Default values if no data is returned

        # Query to calculate the rank of the item within the same description
        rank_sql = """
        SELECT a.ItemName, SUM(a.Total) as Total, SUM(a.count) as Count, 
            RANK() OVER (ORDER BY SUM(a.count) DESC) AS Rank 
        FROM tblorder_detailshistory a, tblorderhistory b 
        WHERE a.order_ID = b.idtblorderHistory 
        AND a.Description = %s 
        AND b.Outlet_Name = %s AND b.bill_no != ''
        GROUP BY a.ItemName
        """
        cursor.execute(rank_sql, (group, outlet,))
        rank_results = cursor.fetchall()


        columns = [col[0] for col in cursor.description]

        rank_results_response = [dict(zip(columns, rows)) for rows in rank_results]

        # Sort the results by 'Rank' in ascending order
        rank_results_responseJson = sorted(rank_results_response, key=lambda x: x['Rank'])
        # Find the rank of the specific item
        item_rank = None
        for row in rank_results:
            if row[0] == item_name:
                item_rank = row[3]
                break


        # Calculate date range for the past month, starting on the same weekday
        today = datetime.now()
        weekday = today.weekday()  # 0=Monday, 6=Sunday
        last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

        # Find the first occurrence of the same weekday in the previous month
        start_date = last_month + timedelta(days=(weekday - last_month.weekday()) % 7)

        print(f"start_date {start_date}")
        start_date_str = start_date.strftime("%Y-%m-%d")
        today_date_str = today.strftime("%Y-%m-%d")
        # Prepare the 7-day interval query
        interval_query = """
        SELECT 
            DATE(MIN(b.Date)) AS Start_Date,
            SUM(a.count) AS Total_Count
        FROM tblorder_detailshistory a
        INNER JOIN tblorderhistory b ON a.order_ID = b.idtblorderHistory
        WHERE a.ItemName = %s 
        AND b.Outlet_Name = %s
        AND b.Date BETWEEN %s AND %s
        AND b.bill_no != ''
        GROUP BY FLOOR(DATEDIFF(b.Date, %s) / 7)
        ORDER BY Start_Date ASC;
        """
        
        # Execute the interval query
        cursor.execute(interval_query, (item_name, outlet, start_date_str, today_date_str, start_date_str))
        interval_results = cursor.fetchall()

        # Process results
        interval_data = []

        # Generate the expected 7-day intervals from start_date to today
        current_start_date = start_date
        intervals = []
        i = 1
        while current_start_date < today:
            current_end_date = current_start_date + timedelta(days=6)
            intervals.append({
                "start_date": current_start_date,
                "end_date": min(current_end_date, today),  # Ensure end_date doesn't go beyond today
                "week": i,
                "total_count": 0  # Default to 0, will update later if data exists
            })
            current_start_date += timedelta(days=7)
            i += 1
        # Map query results for faster lookup
        # Map query results for faster lookup (convert keys to strings)
        query_results = {row[0].strftime("%Y-%m-%d"): row[1] for row in interval_results}  # {start_date_str: total_count}

        print(query_results)

        for key, value in query_results.items():
            result_date = datetime.strptime(key, "%Y-%m-%d").date()
            
            # Find the interval where this date falls
            for interval in intervals:
                if interval["start_date"].date() <= result_date <= interval["end_date"].date():
                    interval["total_count"] += value
                    break

        # Convert start_date and end_date to string for JSON response
        for interval in intervals:
            interval["start_date"] = interval["start_date"].strftime("%Y-%m-%d")
            interval["end_date"] = interval["end_date"].strftime("%Y-%m-%d")

        # Final interval data
        interval_data = intervals

        # Define all months
        all_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Calculate the start and end dates for one year range
        yearly_end_date = datetime.now().date()  # Today's date
        yearly_start_date = yearly_end_date - timedelta(days=366)  # Date one year before



        # Generate a list of months in the desired range
        def get_month_year_range(yearly_start_date, yearly_end_date):
            months = []
            current_date = yearly_start_date.replace(day=1)  # Start from the first day of the month
            while current_date <= yearly_end_date:
                months.append(f"{all_months[current_date.month - 1]} {current_date.year}")
                # Move to the first day of the next month
                if current_date.month == 12:  # December
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)
            return months

        # Get the range of months
        month_year_range = get_month_year_range(yearly_start_date, yearly_end_date)

        # Initialize dictionaries for sales and purchases with the correct range
        sales_data = {
            month_year: {"TotalSales": "0.0", "monthName": month_year, "TotalCount": "0"}
            for month_year in month_year_range
        }

        yearly_start_date_str = yearly_start_date.strftime("%Y-%m-%d")
        yearly_end_date_str = yearly_end_date.strftime("%Y-%m-%d")
        # Example SQL queries to fetch data (replace with actual database execution)
        sql_query_sales = """
            SELECT 
                YEAR(b.Date) AS year,
                MONTH(b.Date) AS month, 
                SUM(a.Total) AS totalSales, 
                SUM(a.count) AS totalCount 

            FROM tblorder_detailshistory a ,tblorderhistory b
            WHERE a.order_ID = b.idtblorderHistory and a.ItemName = %s and b.Date BETWEEN %s AND %s and b.Outlet_Name = %s and b.bill_no != ''
            GROUP BY YEAR(Date), MONTH(Date)
        """
        cursor.execute(sql_query_sales, (item_name, yearly_start_date_str, yearly_end_date_str, outlet,))
        sales_results = cursor.fetchall()
        # Populate sales data
        for year, month, totalSales, totalCount in sales_results:
            month_name = f"{all_months[month - 1]} {year}"  # Combine month and year
            if month_name in sales_data:
                sales_data[month_name] = {"TotalSales": str(totalSales), "monthName": month_name, "TotalCount": str(totalCount)}

        # Convert dictionaries to lists
        sales_json = list(sales_data.values())

        response_data = {
            "Total_Revenue" : total_revenue,
            "Total_Count" : total_count,
            "Group_Ranking" : item_rank,
            "Last_Monthly" : interval_data,
            "Group_AllItem_Ranks": rank_results_responseJson,
            "Yearly_sales_json": sales_json

        }

        return response_data, 200
    
    except mysql.connector.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as error:
        return jsonify({"error": f"Internal server error: {str(error)}"}), 500
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()    
