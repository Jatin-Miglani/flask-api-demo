from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import re


app=Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to flask API"}), 200

def get_db_connection():
    conn=mysql.connector.connect(
        host='localhost',
        user='root',
        password='myMyho2ho99@ .',  # Replace this with your MySQL root password
        database='valyris'
    )
    conn.autocommit = True  # Auto commit transactions (optional)
    return conn

def create_client_tables(client_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Switch to the newly created database
        cursor.execute(f"USE {client_name}")
       # cursor.execute("CREATE TABLE client (id INT AUTO_INCREMENT PRIMARY KEY, client_name VARCHAR(225) " \
       # "NOT NULL UNIQUE, email VARCHAR(225) NOT NULL UNIQUE)")
        cursor.execute("CREATE TABLE company (id INT AUTO_INCREMENT PRIMARY KEY, company_name VARCHAR(255) " \
        "NOT NULL UNIQUE, address VARCHAR(255) NOT NULL, state VARCHAR(255) NOT NULL, contact_person VARCHAR(255) NOT NULL, " \
        "email_id VARCHAR(255) NOT NULL UNIQUE, mobile VARCHAR(255) NOT NULL UNIQUE)")
        cursor.execute("CREATE TABLE user_group (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,user_group_name VARCHAR(255) NOT NULL, " \
        "company_id INT NOT NULL,FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE ON UPDATE CASCADE)")
        cursor.execute("CREATE TABLE user (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, user_name VARCHAR(255) NOT NULL, email_id VARCHAR(255) NOT NULL UNIQUE" \
        ", mobile VARCHAR(255) NOT NULL UNIQUE, company_id INT NOT NULL, user_group_id INT NOT NULL,  FOREIGN KEY (company_id) REFERENCES " \
        "company(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (user_group_id) REFERENCES user_group(id) ON DELETE CASCADE ON UPDATE CASCADE)")
        cursor.execute("CREATE TABLE create_user (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, user_name INT NOT NULL, company_name INT NOT NULL, " \
        "user_group INT NOT NULL, FOREIGN KEY (user_name) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (company_name) REFERENCES " \
        "company(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (user_group) REFERENCES user_group(id) ON DELETE CASCADE ON UPDATE CASCADE)")
        cursor.execute("CREATE TABLE nature (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, nature_name VARCHAR(45) NOT NULL UNIQUE)")
        cursor.execute("INSERT INTO nature (nature_name) VALUES('Task'),('Bug'),('Discussion'),('Issue'),('Meeting'),('Todo')")
        cursor.execute("CREATE TABLE priority (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, priority_name VARCHAR(255) NOT NULL UNIQUE)")
        cursor.execute("INSERT INTO priority (priority_name) VALUES ('High'),('Normal'),('Low')")
        cursor.execute("CREATE TABLE status (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, status_name VARCHAR(255) NOT NULL UNIQUE)")
        cursor.execute("INSERT INTO status(status_name) VALUES ('Draft'),('Active'),('Suspended'),('Completed')")
        cursor.execute("CREATE TABLE project_type (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, name VARCHAR(255) NOT NULL UNIQUE, project_code VARCHAR(255) NOT NULL UNIQUE)")
        cursor.execute("INSERT INTO project_type (name, project_code) VALUES ('Tally','TLY'),('Development','DEV'),('Analysis','AA'),('Web','W')")
        cursor.execute("CREATE TABLE projects (id INT AUTO_INCREMENT PRIMARY KEY, project_type INT NOT NULL, " \
        "project_code VARCHAR(255) NOT NULL UNIQUE, proj_name VARCHAR(255) NOT NULL, start_date DATETIME NOT NULL, end_date DATETIME NOT NULL, " \
        "proj_company INT NOT NULL, proj_manager INT NOT NULL, status INT NOT NULL, priority INT NOT NULL, FOREIGN KEY (project_type) REFERENCES " \
        "project_type(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (proj_company) REFERENCES company(id) ON DELETE CASCADE ON UPDATE CASCADE, " \
        "FOREIGN KEY (proj_manager) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (status) REFERENCES status(id) ON DELETE " \
        "CASCADE ON UPDATE CASCADE, FOREIGN KEY (priority) REFERENCES priority(id) ON DELETE CASCADE ON UPDATE CASCADE)")
        cursor.execute("CREATE TABLE project_task (id INT AUTO_INCREMENT PRIMARY KEY, project_id INT NOT NULL, task_name VARCHAR(255) " \
        "NOT NULL, nature INT NOT NULL, descriiption VARCHAR(255), user INT, user_group INT, start_date DATETIME NOT NULL, " \
        #"end_date DATETIME NOT NULL, " \
        "number INT NOT NULL, duration VARCHAR(45) NOT NULL, status INT NOT NULL, priority INT NOT NULL, sub_task INT, level INT NOT NULL, FOREIGN KEY (project_id) " \
        "REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (nature) REFERENCES nature(id) ON DELETE CASCADE ON UPDATE CASCADE, " \
        "FOREIGN KEY (user) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (user_group) REFERENCES user_group(id) " \
        "ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (status) REFERENCES status(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (priority) REFERENCES " \
        "priority(id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (sub_task) REFERENCES project_task(id) ON DELETE CASCADE ON UPDATE CASCADE)")
        cursor.execute("CREATE TABLE dependencies (task_id INT NOT NULL, depends_on_task_id INT NOT NULL, FOREIGN KEY (task_id) REFERENCES project_task(id) " \
        "ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (depends_on_task_id) REFERENCES project_task(id) ON DELETE CASCADE ON UPDATE CASCADE)")


        return True
    
    except mysql.connector.Error as err:
        return False, str(err)
    
    finally:
        cursor.close()
        conn.close()

@app.route('/create_database', methods=['POST'])
def create_database():

    data=request.get_json()
    client=data.get("name")
    mobile_number=data.get("phone")
    email_id=data.get("email")

    address=data.get("addresses",[])
    single_address = data.get("address")

    h_street = h_city = h_state = h_postal_code = h_country = None
    w_street = w_city = w_state = w_postal_code = w_country = None

    if address:
        for i in address:
            if(i.get("type")=="Home"):
                h_street=i.get("street")
                h_city=i.get("city")
                h_state=i.get("state")
                h_postal_code=i.get("postalCode")
                h_country=i.get("country")
            elif(i.get("type")=="Work"):
                w_street=i.get("street")
                w_city=i.get("city")
                w_state=i.get("state")
                w_postal_code=i.get("postalCode")
                w_country=i.get("country")


    if not client:
        return jsonify({"error": "This field is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)



    cursor.execute("SELECT * from clients_check where client_name = %s and mobile = %s and email_id = %s",(client,mobile_number,email_id,))
    data1=cursor.fetchone()

    if data1:
        return jsonify({"message": "Client already present"}), 200

    cursor.execute("INSERT INTO clients_check (client_name, mobile, email_id, address, h_street, h_city, h_state, h_postal_code, h_country, w_street, " \
    "w_city, w_state, w_postal_code, w_country)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",(client,mobile_number,email_id, single_address, h_street, h_city, h_state, h_postal_code, h_country, w_street, w_city, w_state, w_postal_code, w_country, ))

    c=client
    client = c.strip().replace(" ", "_")

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {client}")

    table_creation = create_client_tables(client)

    if table_creation:
        return jsonify({"message": "Client created successfully"}), 200

    cursor.close()
    conn.close()

@app.route('/fetch_clients', methods=['GET'])
def fetch_clients():

    try:

        conn=get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT client_name from clients_check")

        data=cursor.fetchall()

        client_names=[]
        for client in data:
            client_names.append(client['client_name'])

        return jsonify({"clients": client_names}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        # Make sure to close cursor and connection
        cursor.close()
        conn.close()



@app.route('/add_company', methods=['POST'])
def add_company():
    data = request.get_json()
    client_name = data.get("client_name")
    company_name = data.get("company_name")
    address = data.get("address")
    state = data.get("state")
    contact_person = data.get("contact_person")
    email_id = data.get("email_id")
    mobile = data.get("mobile")
    client='new_databases_clients'

    conn = get_db_connection()  # Ensure you're using the correct database
    cursor = conn.cursor(dictionary=True)

    print(f"Inserting into database: {client_name}")  # Debugging

    if not company_name or not address or not state or not contact_person or not email_id or not mobile:
        return jsonify({"error": "All fields are required!"}), 400

    try:

        cursor.execute(f" USE {client}")

        cursor.execute("SELECT id FROM clients_check WHERE client_name=%s",(client_name,))
        dataa=cursor.fetchone()
        print(dataa['id'])

        if not dataa:
            print("Client not found in DB")
            return ({"error" : "No such client present"}), 400
        
        print("VALUES:", contact_person, email_id, company_name, dataa['id'])

        cursor.execute("INSERT INTO user_company (user_name,email,company_name,client) VALUES (%s,%s,%s,%s)",
                       (contact_person,email_id,company_name,dataa['id'],))
        cursor.execute("INSERT INTO user_create (user,emailid,client,is_client1_comp2) VALUES (%s,%s,%s,%s)",
                       (contact_person,email_id,dataa['id'],2))
        
        print("Ye data added ")
        cursor.execute(f" USE {client_name}")
        query = """
        INSERT INTO company (company_name, address, state, contact_person, email_id, mobile) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (company_name, address, state, contact_person, email_id, mobile)
        cursor.execute("SELECT id FROM company WHERE company_name=%s",(company_name,))
        d=cursor.fetchone()
        print("Look at the values")
        print(d)
        cursor.execute("INSERT INTO user (user_name, email_id, mobile, company_id) VALUES(%s,%s,%s,%s)",(contact_person, email_id, mobile, d['id'],))
        
        cursor.execute(query, values)

        conn.commit()  # Ensure data is committed to the database
        
        print(f"Inserted company: {company_name}")  # Debugging

        return jsonify({"message": "Company created successfully"}), 200

    except Exception as e:
        conn.rollback()  # Rollback if there's an error
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/fetch_companies', methods=["GET"])
def fetch_companies():

    client=request.args.get("client_name")

    if not client:
        return jsonify({"error": "Client must be selected first"}), 400


    try:

        conn=get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"USE {client}")
        cursor.execute("Select company_name from company")

        data1=cursor.fetchall()

        company_names=[]
        for comp in data1:
            company_names.append(comp['company_name'])

        return jsonify({"companies": company_names}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        # Make sure to close cursor and connection
        cursor.close()
        conn.close()



@app.route('/user_group_create', methods=['POST'])
def user_group_create():
    data = request.get_json()
    client_name = data.get("client_name")
    company_name = data.get("company_name")
    user_group_name = data.get("user_group_name")

    print(f"Received Data: Client - {client_name}, Company - {company_name}, User Group - {user_group_name}")

    if not client_name or not company_name or not user_group_name:
        print("Missing required fields!")
        return jsonify({"error": "All fields are required!"}), 400

    try:
        conn = get_db_connection()  # Ensure correct DB selection
        cursor = conn.cursor(dictionary=True)

        cursor.execute("USE {}".format(client_name))  # Ensure correct database

        # Fetch company ID
        cursor.execute("SELECT id FROM company WHERE company_name=%s", (company_name,))
        company = cursor.fetchone()

        if not company:
            print("Company not found!")  # Debugging
            return jsonify({"error": "Company not found"}), 400

        company_id = company["id"]
        print(f"Company ID: {company_id}")  # Debugging

        # Check if the user group already exists
        cursor.execute("SELECT * FROM user_group WHERE user_group_name=%s AND company_id=%s", (user_group_name, company_id))
        existing_group = cursor.fetchone()

        if existing_group:
            print("User group already exists!")  # Debugging
            return jsonify({"error": "User Group already exists"}), 400

        # Insert user group
        query = "INSERT INTO user_group (user_group_name, company_id) VALUES (%s, %s)"
        cursor.execute(query, (user_group_name, company_id))
        conn.commit()
        print(f"Inserted User Group: {user_group_name}")  # Debugging

        return jsonify({"message": "User Group Created Successfully"}), 200

    except Exception as e:
        conn.rollback()  # Rollback if an error occurs
        print(f"Error: {e}")  # Debugging
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/fetch_user_group',methods=['GET'])
def fetch_user_group():

    client=request.args.get("client_name")
    company=request.args.get("company_name")

    if not client:
        return jsonify({"error": "Client must be selected first"}), 400

    if not company:
        return jsonify({"error": "Company must be selected first"}), 400

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"USE {client}")
        cursor.execute("Select user_group_name from user_group where company_id = (SELECT id from company WHERE company_name = %s)",(company,))

        data=cursor.fetchall()

        user_groups=[]
        for group in data:
            user_groups.append(group['user_group_name'])

        return jsonify({"user_groups": user_groups}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        # Make sure to close cursor and connection
        cursor.close()
        conn.close()




@app.route('/insert_user', methods=['POST'])
def insert_user():
    data = request.get_json()
    client = data.get("client_name")
    company = data.get("company_name")
    user_group = data.get("user_group_name")
    user = data.get("user_name")
    emailid = data.get("email_id")
    mobile = data.get("mobile_number")

    print(f"Received Data: Client - {client}, Company - {company}, User Group - {user_group}, User - {user}, Email - {emailid}, Mobile - {mobile}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Ensure the correct database is used
        cursor.execute(f"USE {client}")
        print(f"Using database: {client}")

        # Fetch company ID
        cursor.execute("SELECT id FROM company WHERE company_name=%s", (company,))
        data1 = cursor.fetchone()

        if not data1:
            print("Company not found!")  # Debugging
            return jsonify({"error": "Company not found"}), 400

        d1 = data1['id']
        print(f"Company ID: {d1}")

        # Fetch user group ID
        cursor.execute("SELECT id FROM user_group WHERE user_group_name=%s AND company_id=%s", (user_group, d1))
        data2 = cursor.fetchone()

        if not data2:
            print("User Group not found!")  # Debugging
            cursor.execute("SELECT id FROM user_group WHERE user_group_name=%s", (user_group,))
            data2=cursor.fetchone()
            if not data2:
                return jsonify({"error": "User Group not found"}), 400


        d2 = data2['id']
        print(f"User Group ID: {d2}")

        # Check if the user already exists
        cursor.execute("SELECT * FROM user WHERE user_name=%s AND email_id=%s AND mobile=%s",
                       (user, emailid, mobile,))
        data3 = cursor.fetchone()

        if data3:
            print("User already exists!")  # Debugging

            cursor.execute("SELECT * FROM create_user WHERE user_name=%s AND company_name=%s AND user_group=%s",(data3['id'],d1,d2,))
            dd=cursor.fetchall()
            if not dd:
                cursor.execute("INSERT INTO create_user (user_name, company_name, user_group) VALUES(%s,%s,%s)",(data3['id'],d1,d2,))
                
                return jsonify({"message": "User Created Successfully"}), 200

            return jsonify({"error": "User already exists"}), 400

        # Insert the new user
        query = "INSERT INTO user (user_name, email_id, mobile, company_id, user_group_id) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (user, emailid, mobile, d1, d2))
        cursor.execute("SELECT id FROM user WHERE user_name=%s AND email_id=%s AND mobile=%s AND company_id=%s AND user_group_id=%s",(user,emailid, mobile, d1,d2,))
        dataa=cursor.fetchone()
        cursor.execute("INSERT INTO create_user (user_name,company_name,user_group) VALUES (%s,%s,%s)",(dataa['id'],d1,d2,))
        cursor.execute(f"USE {'new_databases_clients'}")
        cursor.execute("SELECT id FROM clients_check WHERE client_name=%s",(client,))
        dataa1=cursor.fetchone()
        cursor.execute("INSERT INTO user_create (user,emailid,client) VALUES (%s,%s,%s)",(user,emailid,dataa1['id'],))
        conn.commit()  # Ensure data is saved
        print(f"Inserted User: {user}")

        return jsonify({"message": "User Created Successfully"}), 200

    except Exception as e:
        conn.rollback()  # Rollback if there's an error
        print(f"Error: {e}")  # Debugging
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route("/get_machine_detail" , methods=['GET'])
def get_machine_detail():

    data=request.args.get("data_part")

    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM db WHERE data=%s")
    cc=cursor.fetchall()


@app.route ("/mrp",methods=["GET"])
def query():
    db = mysql.connector.connect(
    host="localhost",
    user="rakesh", # Replace with your MySQL username
    password="rakesh", # Replace with your MySQL password
    database="valyris")

##  Select par_item, bom_item, bom_qty, item_nat, mfr_qty from valyris.bom_comp

    cursor = db.cursor (dictionary = True)
    cursor.execute("SELECT par_item as item, bom_item, req_qty as required_qantity, item_unit, mfr_qty as manufacturing_quantity FROM valyris.bom_comp")
    data1=cursor.fetchall()
    return jsonify({"message" : data1})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
                  
