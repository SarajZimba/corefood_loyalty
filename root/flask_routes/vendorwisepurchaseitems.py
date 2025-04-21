from flask import  Blueprint,request, jsonify
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file70 = Blueprint('app_file70',__name__)
from root.auth.check import token_auth
import pytz
from datetime import datetime
import re
from collections import defaultdict

def valid_date(datestring):
        try:
                regex = re.compile("^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$")
                match = re.match(regex, datestring)
                if match is not None:
                    return True
        except ValueError:
            return False
        return False

@app_file70.route("/vendorwise-purchaseitem-lists", methods=["POST"])
@cross_origin()
def stats():
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
        if "dateStart" not in json  or not any([json["dateStart"]])  or json["dateStart"]=="":
            data = {"error":"No startDate provided."}
            return data,400
        if "dateEnd" not in json  or not any([json["dateEnd"]])  or json["dateEnd"]=="":
            data = {"error":"No endDate provided."}
            return data,400
        if "aggregated" not in json  or not any([json["aggregated"]])  or json["aggregated"]=="":
            data = {"error":"No aggregated provided."}
            return data,400
        outlet = json["outlet"]
        dateStart = json["dateStart"]
        dateEnd = json["dateEnd"]
        aggregated = json["aggregated"]
        if not valid_date(dateStart) or not valid_date(dateEnd):
            data={"error":"Invalid date supplied."}
            return data,400
        

        if not token_auth(token):
            data = {"error":"Invalid token."}
            return data,400
        if aggregated == "False":
            purchase_items_query = """select a.Name , a.BrandName, a.UnitsOrdered as ItemCount, a.UOM, a.Rate as ItemRate, (a.Rate*a.UnitsOrdered) as Total ,b.Outlet_PurchaseReqID, b.Company_Name, b.purchaseBillNumber from intbl_purchaserequisition_contract a , intbl_purchaserequisition b where a.PurchaseReqID = b.IDIntbl_PurchaseRequisition and b.ReceivedDate between %s and %s and b.Outlet_Name = %s"""
        elif aggregated == "True":
            purchase_items_query = """select a.Name , a.BrandName, sum(a.UnitsOrdered) as ItemCount, a.UOM, AVG(a.Rate) as ItemRate, sum((a.Rate) * (a.UnitsOrdered)) as Total, b.Company_Name from intbl_purchaserequisition_contract a , intbl_purchaserequisition b where a.PurchaseReqID = b.IDIntbl_PurchaseRequisition and b.ReceivedDate between %s and %s and b.Outlet_Name = %s group by a.Name, b.Company_Name"""
        else:
            data = {"error":"Invalid aggregated value provided."}
            return data, 400
        cursor.execute(purchase_items_query, (dateStart, dateEnd, outlet,))

        # results = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]  # Extract column names
        results = [dict(zip(columns, row)) for row in cursor.fetchall()] 
        # print(results)
        response_data = {}

        # for result in results:
        for result in results:
            if result["Company_Name"] not in response_data:
                response_data[result["Company_Name"]] = []
            result["ItemRate"] = round(result["ItemRate"], 2)
            result["Total"] = round(result["Total"], 2)
            # result["ItemRate"] = round(result["ItemRate"], 2)
            response_data[result["Company_Name"]].append(result)

        response = []
        for vendor, value in response_data.items():
            total = sum(float(item["Total"]) for item in value)
            vendor_data = {
                "vendor": vendor,
                "items": value,
                "total": round(total, 2)
            }

            response.append(vendor_data)

        return response, 200

        

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


