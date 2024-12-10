from flask import Flask,render_template,request,jsonify
import pandas as pd
import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import random
import os

app = Flask(__name__)

#----------------forgrt password-------------

code = random.randint(100000 , 999999)
#code=111111
def send_mail(name):
    # Email configuration
    global email 
    email=name
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    USERNAME = 'teamswades6@gmail.com'
    PASSWORD = 'pjmn yufk qowm ofdh'
    FROM_EMAIL = 'teamswades6@gmail.com'
    TO_EMAIL = email
    SUBJECT = 'OTP verification - ' + datetime.now().strftime('%Y-%m-%d')
    internet_connection_error = False
    def create_email_body():
        # Create the body of the email
        # You can customize this function to generate your report
        body=f"""Dear User,\n To ensure the security of your account, One-Time Password (OTP) for your recent request.\n\nYour Verificiation code [ {code} ]\n The code is valid for the next '5' minutes, Don't share with others\n\n\nStay secure\n\nFrom,\nTeam SWADES"""
        return body

    def send_email(subject, body):
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
    
        # Attach the body text
        msg.attach(MIMEText(body, 'plain'))
    
        try:
            # Set up the server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Secure the connection
            server.login(USERNAME, PASSWORD)  # Login to the email account
            
            # Send email
            server.send_message(msg)
            print(f"Email sent successfully to {TO_EMAIL}")
    
        except Exception as e:
            print(f"Failed to send email: {e}")

        finally:
            server.quit()  # Terminate the SMTP session

    body = create_email_body()
        # Send the email
    try:
        send_email(SUBJECT, body)
    except UnboundLocalError:
        internet_connection_error=True
    return internet_connection_error


#    ----    start   -----

@app.route('/')
def index():
    return render_template('/Autentication/login.html')
    #return render_template('head.html')


## email verification

@app.route('/forget')
def forget():
    return render_template('/Autentication/forget.html')


@app.route('/checking_details',methods=['POST'])
def checking_details():
    email=request.form['email']
    password=request.form['password']
    data=data_retrive()
    c=0
    for mail,code,role in data:
        if(mail==email and code==password):
            global user_role
            user_role = role
            print(user_role)
            c+=1
    if(c==0):

        return render_template("/Autentication/login.html",warning=True)
    else:
        if user_role=='head':
            return render_template('head.html')
        elif user_role=='division':
            return render_template('Division/division_home.html')
        elif user_role=="region":
            return render_template('/Regional_level/home.html')
        elif user_role=='branch':
            return render_template('branch.html')

        


## Database connection
def data_retrive():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="10081008",
            database="swades"
        )
        sql = "SELECT * FROM users;"
        mycursor = mydb.cursor()
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        return myresult
        
    except Error as e:
        print(f"Error connecting to database: {e}")
        return []


@app.route('/get_mail_id',methods=['POST'])
def user_mail():
    mail_id=request.form['email']
    internet_connection_error=send_mail(mail_id)
    if internet_connection_error:
        return render_template('/Autentication/forget.html',internet=True)
    else:
        return render_template('/Autentication/otp.html')


@app.route('/checking_otp',methods=['POST'])
def checking_otp():
    user_code=request.form['text']
    if int(user_code)==code:
        return render_template('/Autentication/newpassword.html',user_email_id={email})
    else:
        return render_template('/Autentication/otp.html',invalid=True)


@app.route('/newpassword',methods=['POST'])
def newpassword():
    password1=request.form['password1']
    password2=request.form['password2']
    print("mail_id ",email)
    if password1==password2:
        data=data_retrive()
        for mail,code,roles in data:
            if mail==email:
                try:
                    connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="10081008",
                    database="swades"
                    )
                    if connection.is_connected():
                        cursor = connection.cursor()
                        insert_query = "UPDATE users SET `password` = %s WHERE email = %s"
                        cursor.execute(insert_query, (password1, email))
                        connection.commit()
                        print("Password updated successfully.")

                except Error as e:
                    print(f"Error: {e}")
                finally:
                    if cursor:
                        cursor.close()
                    if connection and connection.is_connected():
                        connection.close()
                        return render_template('/Autentication/login.html')
            else:
                return render_template('/Autentication/newpassword.html',different=True)




@app.route('/overview')
def overview():
    
    if user_role=='head':
        return render_template('head.html')
    elif user_role=='division':
        return render_template('Division/division_overview.html')
    elif user_role=="region":
        return render_template('Regional_level/region.html')
    elif user_role=='branch':
        return render_template('branch.html')

@app.route('/home')
def whatsapp():
    return render_template('Regional_level/home.html')

@app.route('/login')
def login():
    return render_template('/Autentication/login.html')

@app.route('/register')
def register():
    return render_template('/Autentication/register.html')

@app.route('/into_database',methods=['POST'])
def intoDatabase():
    email=request.form['email']
    password=request.form['password']
    role_type = request.form['role_type']
    data=data_retrive()
    connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="10081008",
            database="swades")
    try:
        cursor = connection.cursor()
        insert_query = "INSERT INTO users (email,password,roles) VALUES (%s,%s,%s)"
        cursor.execute(insert_query, (email,password,role_type))
        connection.commit()
        cursor.close()
        connection.close()
        return render_template("/Autentication/login.html")
    except mysql.connector.errors.IntegrityError:
        return render_template("/Autentication/register.html",error=True)
    
    

##        Demographic SECTORS
demographic_data = pd.read_csv('circle_level.csv')
@app.route('/demographic')
def demographic():
    return render_template("Regional_level/demographic.html")
@app.route('/get_columns_demographic', methods=['POST'])
def get_columns():
    demographic = request.json.get('demographic')
    columns_mapping = {
        "Population": ["Population", "Male", "Female"],
        "Scheduled Castes (SC)": ["SC", "Male_SC", "Female_SC"],
        "Scheduled Tribes (ST)": ["ST", "Male_ST", "Female_ST"],
        "Age Groups": ["Age_Group_0_29", "Age_Group_30_49", "Age_Group_50", "Age_not_stated"],
        "Gender Ratios": ["Male", "Female"]
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_demographic', methods=['POST'])
def generate_result():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = demographic_data[['Region', 'District name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }
    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })


##                     Housing Sector

housing_data = pd.read_csv('circle_level.csv')
@app.route('/housing')
def housing():
    return render_template("Regional_level/housing.html")
@app.route('/get_columns_housing', methods=['POST'])
def get_columns_housing():
    demographic = request.json.get('demographic')
    columns_mapping = {
        "Housing Characteristics": ["Households", "Rural_Households", "Urban_Households"],
        "Household Sizes": ["Household_size_1_person_Households", "Household_size_2_persons_Households", "Household_size_1_to_2_persons","Household_size_3_persons_Households","Household_size_3_to_5_persons_Households","Household_size_4_persons_Households","Household_size_5_persons_Households","Household_size_6_8_persons_Households","Household_size_9_persons_and_above_Households"],
        "Ownership": ["Ownership_Owned_Households", "Ownership_Rented_Households"],
        "Condition of Houses": ["Condition_of_occupied_census_houses_Dilapidated_Households"]
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_housing', methods=['POST'])
def generate_result_housing():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = housing_data[['Region', 'District name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }

    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })



##                     Education Sector

education_data = pd.read_csv('circle_level.csv')
@app.route('/education')
def education():
    return render_template("Regional_level/education.html")
@app.route('/get_columns_education', methods=['POST'])
def get_columns_education():
    demographic = request.json.get('demographic')
    columns_mapping = {
        "Literacy Levels": ["Literate", "Illiterate_Education"],
        "Education Levels": ["Below_Primary_Education", "Primary_Education", "Middle_Education","Secondary_Education","Higher_Education","Graduate_Education","Other_Education","Literate_Education","Total_Education"],
        "Gendered Literacy": ["Male_Literate", "Female_Literate"]
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_education', methods=['POST'])
def generate_result_education():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = education_data[['Region', 'District name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }

    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })


##                  Infrastructure

infrastructure_data = pd.read_csv('circle_level.csv')
@app.route('/infrastructure')
def infrastructure():
    return render_template("Regional_level/infrastructure.html")
@app.route('/get_columns_infrastructure', methods=['POST'])
def get_columns_infrastructure():
    demographic = request.json.get('demographic')
    columns_mapping = {
        "Basic Amenities": ["LPG_or_PNG_Households", "Households_with_Electric_Lighting", "Households_with_Internet","Households_with_Computer"],
        "Sanitation": ["Having_bathing_facility_Total_Households", "Not_having_bathing_facility_within_the_premises_Total_Households", "Having_latrine_facility_within_the_premises_Total_Households","Not_having_latrine_facility_within_the_premises_Alternative_source_Open_Households"],
        "Water Supply": ["Main_source_of_drinking_water_Tapwater_Households", "Main_source_of_drinking_water_Tubewell_Borehole_Households", "Main_source_of_drinking_water_Un_covered_well_Households","Main_source_of_drinking_water_Spring_Households","Main_source_of_drinking_water_River_Canal_Households","Main_source_of_drinking_water_Tank_Pond_Lake_Households","Main_source_of_drinking_water_Other_sources_Households"],
        "Drinking Water Source Locations": ["Location_of_drinking_water_source_Within_the_premises_Households", "Location_of_drinking_water_source_Near_the_premises_Households"]
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_infrastructure', methods=['POST'])
def generate_result_infrastructure():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = infrastructure_data[['Region', 'District name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }
    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable
    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })


##                  Transportation Sector

transportation_data = pd.read_csv('circle_level.csv')
@app.route('/transportation')
def transportation():
    return render_template("Regional_level/transportation.html")
@app.route('/get_columns_transportation', methods=['POST'])
def get_columns_transportation():
    demographic = request.json.get('demographic')
    columns_mapping = {
        "Transportation Access": ["Households_with_Bicycle", "Households_with_Car_Jeep_Van", "Households_with_Scooter_Motorcycle_Moped"],
        "Communication Access": ["Households_with_Radio_Transistor", "Households_with_Telephone_Mobile_Phone_Landline_only", "Households_with_Telephone_Mobile_Phone_Mobile_only","Households_with_Telephone_Mobile_Phone","Households_with_Telephone_Mobile_Phone_Both"]  
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_transportation', methods=['POST'])
def generate_result_transportation():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = transportation_data[['Region', 'District name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }

    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })

##                                 Circle Level sector

circle_data = pd.read_csv('circle_level.csv')
@app.route('/circle')
def circle_level():
    return render_template("Regional_level/circle.html")
@app.route('/get_columns_circle', methods=['POST'])
def get_columns_circle():
    # Dynamically fetch all column names except 'Region'
    column_names = [column for column in circle_data.columns if column != "Region"]
    return jsonify(column_names)
@app.route('/generate_result_circle', methods=['POST'])
def generate_result_circle():
    region = request.json.get('region')  # Updated to accept JSON input
    column = request.json.get('column')  # Column selected
    graph_type = request.json.get('graph')  # Graph type

    # Filter data based on selected region and column
    filtered_data = circle_data[circle_data['Region'] == region][['Region', 'District name', column]]
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }

    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data,
        "graph_type": graph_type
    })



##                 DIVISIONS


@app.route('/division_report')
def division_report():
    return render_template('Division/division_report.html')

@app.route('/division_home')
def division_home():
    return render_template('Division/division_home.html')



##                 Demographic Division

demographic_division_data = pd.read_csv('Vijayawada Division.csv')
@app.route('/demographic_division')
def demographic_division():
    return render_template('Division/division_demographic.html')
@app.route('/get_columns_demographic_division', methods=['POST'])
def get_columns_demographic_division():
    demographic = request.json.get('demographic')
    columns_mapping = {
       "Population": [
            "Total Population", "Rural population", "Urban population", 
            "Rural Male Population", "Rural Female Population"
            ],
            "Sex Ratios": [
            "Sex Ratio for Adults", "Rural Sex Ratio for Adults", 
            "Urban Sex Ratio for Adults"
            ],
            "Age Group (0-6 years)": [
            "Age Group 0_6", "Age Group rural 0_6", "Age Group Urban 0_6"
            ],
            "Gendered Age Group (0-6 years)": [
            "0_6 age Boys population", "0_6 age Rural Boys population", 
            "0_6 age Urban Boys population", "0_6 age Girls population", 
            "0_6 age Rural Girls population", "0_6 age Urban Girls population"
            ],
            "Sex Ratios for (0-6 years)": [
            "Sex Ratio for 0-6", "Rural Sex Ratio for 0-6", "Urban Sex Ratio for 0-6"
            ]
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_demographic_division', methods=['POST'])
def generate_result_demographic_division():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = demographic_division_data[['Division', 'City/Village Name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }

    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })



##                    Economic Division

economic_division_data = pd.read_csv('Vijayawada Division.csv')
@app.route('/economic_division')
def economic_division():
    return render_template('Division/division_economic.html')
@app.route('/get_columns_economic_division', methods=['POST'])
def get_columns_economic_division():
    demographic = request.json.get('demographic')
    columns_mapping = {
          "Workforce": [
            "Cultivators Male Workers", "Cultivators Female workers", 
            "Total Male Workers (Main+Marginal)", "Total Female workers(Main+Marginal)", 
            "Agricultural Labour's Female Workers", "Agriculture Labours Male Workers", 
            "Household Male Workers", "Household Female Workers", 
            "Male Other Workers", "Female Other Workers"
            ],
            "Non-Workers": [
            "Male Non-Workers", "Female Non-Workers"
            ],
            "Workforce by Type": [
            "Male Main Workers", "Female Main Workers", 
            "Male Marginal Workers", "Female Marginal Workers"
            ]
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_economic_division', methods=['POST'])
def generate_result_economic_division():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = economic_division_data[['Division', 'City/Village Name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }

    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })



##                 Education Division

education_division_data = pd.read_csv('Vijayawada Division.csv')
@app.route('/education_division')
def education_division():
    return render_template('Division/division_education.html')
@app.route('/get_columns_education_division', methods=['POST'])
def get_columns_education_division():
    demographic = request.json.get('demographic')
    columns_mapping = {
        "Literacy": [
            "Literates", "Rural Literates", "Urban Literates", 
            "Male Literates", "Rural Male literates", "Urban Male Literates", 
            "Female Literates", "Female Rural Literates", "Female Urban Literates"
            ],
            "Illiteracy": [
            "illiterates", "Rural illiterates", "Urban illiterates", 
            "Male illiterates", "Rural Male illiterates", "Urban Male illiterates", 
            "Female illiterates", "Female Rural illiterates", "Female Urban illiterates"
            ],
            "Literacy Rates": [
            "Literacy rate", "Rural Literacy rate", "Urban Literacy rate", 
            "Male Literacy rate", "Rural Male Literacy rate", "Urban Male Literacy rate", 
            "Female Literacy rate", "Female Rural Literacy rate", "Female Urban Literacy rate"
            ]
    }
    return jsonify(columns_mapping.get(demographic, []))
@app.route('/generate_result_education_division', methods=['POST'])
def generate_result_education_division():
    demographic = request.form['demographic']
    column = request.form['column']
    graph_type = request.form['graph']

    # Filter data based on selected demographic and column
    filtered_data = education_division_data[['Division', 'City/Village Name', column]]  # Limit rows for simplicity in demo
    summary = {
        "mean": float(filtered_data[column].mean()),  # Convert to Python float
        "sum": float(filtered_data[column].sum()),    # Convert to Python float
        "count": int(filtered_data[column].count())   # Convert to Python int
    }

    # Convert DataFrame to JSON serializable format
    data_records = filtered_data.to_dict(orient='records')
    graph_data = filtered_data[column].astype(float).tolist()  # Ensure graph data is JSON-serializable

    return jsonify({
        "summary": summary,
        "data": data_records,
        "graph_data": graph_data
    })



if __name__ == '__main__':
    app.run(port=9000)
