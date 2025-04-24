from flask import Blueprint, request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

app_file8 = Blueprint("app_file8", __name__)


@app_file8.route("/postsales", methods=["POST"])
@cross_origin()
def stats():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute("USE {};".format(os.getenv("database")))

        data = request.get_json()

        if not data:
            return {"error": "Missing or invalid JSON body"}, 400

        # Insert into tblorderhistory
        insert_order_sql = """
            INSERT INTO tblorderhistory (
                Outlet_OrderID, Employee, Table_No, NoOfGuests, Start_Time, End_Time, State, Type,
                Discounts, Date, bill_no, Total, serviceCharge, VAT, DiscountAmt, PaymentMode,
                fiscal_year, GuestName, Outlet_Name, billPrintTime, guestID, guestEmail,
                guestPhone, guestAddress, order_id_ocular
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            insert_order_sql,
            (
                data["OrderID"],
                data["Employee"],
                data["TableNo"],
                data["noofGuest"],
                data["start_Time"],
                data["end_Time"],
                data["state"],
                data["type"],
                data["discounts"],
                data["date"],
                data["bill_No"],
                data["Total"],
                data["serviceCharge"],
                data["VAT"],
                data["discountAmt"],
                data["paymentMode"],
                data["fiscal_Year"],
                data["GuestName"],
                data["Outlet_Name"],
                data["billPrintTime"],
                data["guestID"],
                data["guestEmail"],
                data["guestPhone"],
                data["guestAddress"],
                data.get("order_id_ocular", None),
            ),
        )
        mydb.commit()

        # Handle Credit Entry
        if data["paymentMode"] == "Credit":
            credit_sql = """
                INSERT INTO CreditHistory (outetName, Date, customerName, guestID, creditState, Outlet_OrderID, Amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                credit_sql,
                (
                    data["Outlet_Name"],
                    data["date"],
                    data["GuestName"],
                    data["guestID"],
                    "InitialEntry",
                    data["OrderID"],
                    data["Total"],
                ),
            )
            mydb.commit()

        # Get order ID for item insertion
        cursor.execute(
            "SELECT idtblorderhistory FROM tblorderhistory ORDER BY idtblorderhistory DESC LIMIT 1"
        )
        order_id = cursor.fetchone()[0]

        # Insert each item into tblorder_detailshistory
        insert_item_sql = """
            INSERT INTO tblorder_detailshistory (
                order_ID, ItemName, itemRate, Total, ItemType, Description, discountExempt, count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        for item in data["ItemDetailsList"]:
            item_data = (
                order_id,
                item["itemName"],
                item["ItemRate"],
                item["total"],
                item["ItemType"],
                item["Description"],
                item["disExempt"],
                item["count"],
            )
            cursor.execute(insert_item_sql, item_data)
            mydb.commit()

        if data["guestPhone"] != "":

            loyalty_received_check_query = """SELECT * FROM loyaltyqueue WHERE outlet = %s and bill_no = %s and date= %s"""
            cursor.execute(
                loyalty_received_check_query,
                (
                    data["Outlet_Name"],
                    data["bill_No"],
                    data["date"],
                ),
            )
            loyalty_received_record = cursor.fetchone()
            print(loyalty_received_record)
            if not loyalty_received_record or (loyalty_received_record[3] and loyalty_received_record[3].lower() == "pending"):
                # Check and Insert Guest if not exists
                guest_check_query = """
                    SELECT * FROM guest WHERE guestPhone = %s
                """
                cursor.execute(guest_check_query, (data["guestPhone"],))
                guest_record = cursor.fetchone()
                print("guest recrd", guest_record)
                if not guest_record:
                    insert_guest_query = """
                        INSERT INTO guest (guestID, guestEmail, guestPhone, guestAddress, Outlet_Name, GuestName, loyalty_points)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        insert_guest_query,
                        (
                            data["guestID"],
                            data["guestEmail"],
                            data["guestPhone"],
                            data["guestAddress"],
                            data["Outlet_Name"],
                            data["GuestName"],
                            0.00,
                        ),
                    )
                    mydb.commit()

                print("Outlet name is", data["Outlet_Name"])

                # Loyalty points logic
                cursor.execute(
                    "SELECT loyalty_percent FROM outetnames WHERE Outlet = %s",
                    (data["Outlet_Name"],),
                )

                loyalty_result = cursor.fetchone()
                loyalty_percent = (
                    loyalty_result[0] if loyalty_result and loyalty_result[0] else 0.0
                )

                if loyalty_percent > 0:
                    loyalty_earned = (
                        float(data["Total"] - data["VAT"]) * float(loyalty_percent)
                    ) / 100

                    # Get previous points
                    cursor.execute(
                        """
                        SELECT loyalty_points FROM guest 
                        WHERE guestID = %s AND GuestName = %s AND Outlet_Name = %s
                    """,
                        (data["guestID"], data["GuestName"], data["Outlet_Name"]),
                    )
                    prev_points_result = cursor.fetchone()
                    prev_points = (
                        float(prev_points_result[0]) if prev_points_result else 0.00
                    )

                    new_total_points = round(prev_points + loyalty_earned, 2)

                    # Update guest's total loyalty points
                    update_loyalty_query = """
                        UPDATE guest
                        SET loyalty_points = %s
                        WHERE guestID = %s AND GuestName = %s AND Outlet_Name = %s
                    """
                    cursor.execute(
                        update_loyalty_query,
                        (
                            new_total_points,
                            data["guestID"],
                            data["GuestName"],
                            data["Outlet_Name"],
                        ),
                    )
                    mydb.commit()

                    # Insert history
                    insert_loyalty_history = """
                        INSERT INTO GuestLoyaltyHistory (
                            guestID, GuestName, Outlet_Name, Date, PreviousPoints, EarnedPoints, TotalPoints, phone_no
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        insert_loyalty_history,
                        (
                            data["guestID"],
                            data["GuestName"],
                            data["Outlet_Name"],
                            data["date"],
                            round(prev_points, 2),
                            round(loyalty_earned, 2),
                            new_total_points,
                            data["guestPhone"]                            
                        ),
                    )
                    mydb.commit()

                    # LoyaltyQueue update or insert
                    loyaltyqueue_pending_check_query = """
                        SELECT id FROM loyaltyqueue 
                        WHERE outlet = %s AND bill_no = %s AND date = %s and status='pending'
                    """
                    cursor.execute(
                        loyaltyqueue_pending_check_query,
                        (data["Outlet_Name"], data["bill_No"], data["date"]),
                    )
                    loyalty_row = cursor.fetchone()

                    if loyalty_row:
                        # Update existing entry to received if it was pending
                        update_loyalty_status = """
                            UPDATE loyaltyqueue
                            SET status = 'received'
                            WHERE outlet = %s AND bill_no = %s AND date = %s AND status = 'pending'
                        """
                        cursor.execute(
                            update_loyalty_status,
                            (data["Outlet_Name"], data["bill_No"], data["date"]),
                        )
                        mydb.commit()
                    else:
                        # Insert new entry marked as received
                        insert_loyalty_entry = """
                            INSERT INTO loyaltyqueue (hash_code, status, outlet, bill_no, sub_total, date)
                            VALUES ( %s, 'received', %s, %s, %s, %s)
                        """
                        import hashlib

                        hash_input = (
                            f"{data['bill_No']}{data['Outlet_Name']}{data['date']}"
                        )
                        hash_code = hashlib.sha256(hash_input.encode()).hexdigest()

                        cursor.execute(
                            insert_loyalty_entry,
                            (
                                hash_code,
                                data["Outlet_Name"],
                                data["bill_No"],
                                data["Total"],  # Using total as sub_total here
                                data["date"],
                            ),
                        )
                        mydb.commit()
        mydb.close()
        return {"success": "Data posted successfully"}

    except Exception as error:
        return {"error": str(error)}, 400
