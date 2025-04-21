from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()

app_file43 = Blueprint('app_file43', __name__)
from root.auth.check import token_auth

from .postintosalesproportal import updateuserinsalesproportal

@app_file43.route('/edituser', methods=['POST'])
@cross_origin()
def edit_user():
    try:
        # Connect to the database
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database')
        )
        cursor = mydb.cursor(buffered=True)

        # Get JSON data from the request
        json = request.get_json()

        # Validate input fields
        if "token" not in json or not json["token"]:
            return {"error": "No token provided"}, 400

        if "username" not in json or not json["username"]:
            return {"error": "No username provided"}, 400
        
        if "restaurantURL" not in json or not json["restaurantURL"] or "baseURL" not in json:
            return {"error": "Some urls not provided"}, 400

        if not token_auth(json["token"]):
            return {"error": "Invalid token"}, 400

        if "new_username" not in json and "new_password" not in json and "new_type" not in json:
            return {"error": "No fields to update provided"}, 400
        if json.get("new_username")== "": 
            return {"error": "Username cannot be empty"}, 400
        if json.get("new_password")== "": 
            return {"error": "Password cannot be empty"}, 400
        if json.get("new_type")== "": 
            return {"error": "Type cannot be empty"}, 400

        # Prepare variables
        username = json["username"]
        new_username = json.get("new_username", None)
        new_password = json.get("new_password", None)
        new_type = json.get("new_type", None)
        restaurantURL = json["restaurantURL"]
        baseURL = json["baseURL"]

        get_sql = f"""select * from EmployeeLogin where username=%s"""
        cursor.execute(get_sql,(username,),)
        temp_sql_data= cursor.fetchall()
        if temp_sql_data ==[]:
            cursor.close()
            mydb.close()
            data = {'error':'No User found of that username'}
            return data, 400

        # Create the SQL query to update fields dynamically
        update_fields = []
        values = []

        if new_username:
            update_fields.append("userName = %s")
            values.append(new_username)
        if new_password:
            update_fields.append("password = %s")
            values.append(new_password)
        if new_type:
            update_fields.append("type = %s")
            values.append(new_type)

        if not update_fields:
            return {"error": "No valid fields to update"}, 400

        # Add the username condition to the query
        update_query = f"UPDATE EmployeeLogin SET {', '.join(update_fields)} WHERE userName = %s"
        values.append(username)

        # Execute the query
        cursor.execute(update_query, tuple(values))
        mydb.commit()

        # if cursor.rowcount == 0:
        #     return {"error": "No user found with the provided username"}, 404
        

        if new_type == "admin":
            updateAccountingsalespro_data = {
                "old_username": username,
                "username": new_username,
                "password": new_password,
                "restaurantURL": restaurantURL,
                "baseURL": baseURL
            }

            updateuserinsalesproportal(updateAccountingsalespro_data)

        return {"success": "User details updated successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()
