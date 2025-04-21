from flask import  Blueprint, request
import mysql.connector
from flask_cors import  cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file14= Blueprint('app_file14',__name__)


def addDatatoDict(dicdata=0, data=0):
    _data = []
    for i in range(len(data)):
        if len(dicdata[i]) != 0:
            temp = data[i]
            temp1 = dicdata[i]
            key = temp1.keys()
            value = temp1.values()
            a = list(key)
            b = list(value)
            temp[a[0]] = float(b[0])
            _data.append(temp)
        else:
            _data.append(data[i])
    return _data



@app_file14.route("/reqdetails/<int:id>", methods=["GET"])
@cross_origin()
def reqdetails(id):
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        sql = f"""
        select * from intbl_purchaserequisition_contract where PurchaseReqID=%s ORDER BY ItemID DESC;
        """
        # if not id.isdigit():
        #     data={"error":"Limit must be an integer"}
        #     return data,400
        cursor.execute(sql,(id,),)
        desc = cursor.description
        data =[dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
        query = []
        for item in data:
            sql = f"""SELECT Rate as last_purchase FROM `intbl_purchaserequisition_contract` WHERE ItemID ={item['ItemID']} and PurchaseReqID !={id} order by PurchaseReqID desc limit 1;"""
            query.append(sql)
        _list = []
        for items in query:
            cursor.execute(items)
            desc = cursor.description
            listdata = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            _list.append(listdata)
        _data = []
        for i in range(0, len(_list)):
            if len(_list[i]) == 0:
                _data.append({"last_purchase": 0})
            else:
                _data.append(_list[i][0])
        data = addDatatoDict(_data, data)
        data =  {"intbl_purchaserequisition_contract": data}
        mydb.close()
        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400



# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()
# app_file14 = Blueprint('app_file14', __name__)

# def addDatatoDict(dicdata=0, data=0):
#     _data = []
#     for i in range(len(data)):
#         if len(dicdata[i]) != 0:
#             temp = data[i]
#             temp1 = dicdata[i]
#             key = temp1.keys()
#             value = temp1.values()
#             a = list(key)
#             b = list(value)
#             temp[a[0]] = float(b[0])
#             _data.append(temp)
#         else:
#             _data.append(data[i])
#     return _data

# @app_file14.route("/reqdetails/<int:id>", methods=["GET"])
# @cross_origin()
# def reqdetails(id):
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'), 
#             user=os.getenv('user'), 
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)
#         outlet_name = request.args.get("outlet_name", "")
#         limit = request.args.get("limit", 5)  # Default limit to 5 if not provided        
#         # Fetch main data
#         sql = f"""
#         SELECT *,       (
#                     SELECT 
#                         Rate 
#                     FROM 
#                         intbl_purchaserequisition_contract 
#                     WHERE 
#                         ItemID = a.ItemID 
#                         AND PurchaseReqID != a.PurchaseReqID 
#                     ORDER BY 
#                         PurchaseReqID DESC 
#                     LIMIT 1
#                 ) AS last_purchase FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b 
#                 WHERE a.PurchaseReqID=%s AND b.Outlet_Name = %s 
#         ORDER BY ItemID DESC;
#         """
#         cursor.execute(sql, (id,outlet_name,))
#         desc = cursor.description
#         data = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
        
#         # Prepare to fetch history for each item
#         for item in data:
#             item_id = item['ItemID']

            
#             if outlet_name:
#                 sql = f"""
#                 SELECT a.rate, a.UnitsOrdered, b.ReceivedDate
#                 FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b 
#                 WHERE a.PurchaseReqID = b.IDIntbl_PurchaseRequisition 
#                 AND a.ItemID = %s 
#                 AND b.Outlet_Name = %s 
#                 ORDER BY a.PurchaseReqID DESC 
#                 LIMIT %s;
#                 """
#                 cursor.execute(sql, (item_id, outlet_name, int(limit)))
#                 history_desc = cursor.description
#                 history_data = [
#                     dict(zip([col[0] for col in history_desc], row)) 
#                     for row in cursor.fetchall()
#                 ]
#                 item['history'] = history_data  # Add history data to the item block
#             else:
#                 item['history'] = []
#             item['outlet_name'] = outlet_name

#         # data['outlet_name'] = outlet_name

#         data = {"intbl_purchaserequisition_contract": data}
#         mydb.close()
#         return data, 200

#     except Exception as error:
#         data = {'error': str(error)}
#         return data, 400


# added grn
# from flask import Blueprint, request
# import mysql.connector
# from flask_cors import cross_origin
# import os
# from dotenv import load_dotenv

# load_dotenv()
# app_file14 = Blueprint('app_file14', __name__)

# def addDatatoDict(dicdata=0, data=0):
#     _data = []
#     for i in range(len(data)):
#         if len(dicdata[i]) != 0:
#             temp = data[i]
#             temp1 = dicdata[i]
#             key = temp1.keys()
#             value = temp1.values()
#             a = list(key)
#             b = list(value)
#             temp[a[0]] = float(b[0])
#             _data.append(temp)
#         else:
#             _data.append(data[i])
#     return _data

# @app_file14.route("/reqdetails/<int:id>", methods=["GET"])
# @cross_origin()
# def reqdetails(id):
#     try:
#         mydb = mysql.connector.connect(
#             host=os.getenv('host'), 
#             user=os.getenv('user'), 
#             password=os.getenv('password')
#         )
#         cursor = mydb.cursor(buffered=True)
#         database_sql = "USE {};".format(os.getenv('database'))
#         cursor.execute(database_sql)

#         # sql = f"""
#         # SELECT * FROM intbl_purchaserequisition_contract 
#         # WHERE PurchaseReqID=%s 
#         # ORDER BY ItemID DESC;
#         # """
#         outlet_name = request.args.get("outlet_name", "")
#         limit = request.args.get("limit", 5)  # Default limit to 5 if not provided  
#         # Fetch main data
#         sql = f"""
#         SELECT * FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b 
#         WHERE a.PurchaseReqID=%s AND b.Outlet_Name = %s 
#         ORDER BY ItemID DESC;
#         """
#         cursor.execute(sql, (id,outlet_name,))
#         desc = cursor.description
#         data = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
        
#         # Prepare to fetch history for each item
#         for item in data:
#             item_id = item['ItemID']

            
#             if outlet_name:
#                 sql = f"""
#                 SELECT a.rate, a.UnitsOrdered, b.ReceivedDate 
#                 FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b 
#                 WHERE a.PurchaseReqID = b.IDIntbl_PurchaseRequisition 
#                 AND a.ItemID = %s 
#                 AND b.Outlet_Name = %s 
#                 ORDER BY a.PurchaseReqID DESC 
#                 LIMIT %s;
#                 """
#                 cursor.execute(sql, (item_id, outlet_name, int(limit)))
#                 history_desc = cursor.description
#                 history_data = [
#                     dict(zip([col[0] for col in history_desc], row)) 
#                     for row in cursor.fetchall()
#                 ]
#                 item['history'] = history_data  # Add history data to the item block
#             else:
#                 item['history'] = []
#             item['outlet_name'] = outlet_name

#         # data['outlet_name'] = outlet_name

#         grn_sql = f"""
#         SELECT GRN FROM intbl_purchaserequisition_contract a, intbl_purchaserequisition b 
#         WHERE a.PurchaseReqID=%s AND b.Outlet_Name = %s ;
#         """

#         # Execute the query
#         cursor.execute(grn_sql, (id,outlet_name,))

#         # Fetch the result (since you expect only one result)
#         grn_result = cursor.fetchone()

#         # Check if the result is not None and extract the GRN value
#         grn = 0
#         if grn_result:
#             grn = grn_result[0]

#         data = {"intbl_purchaserequisition_contract": data, "grn": grn}
#         mydb.close()
#         return data, 200

#     except Exception as error:
#         data = {'error': str(error)}
#         return data, 400
