import streamlit as st
from pymongo import MongoClient
from PIL import Image
import io
import datetime
import base64

# MongoDB connection
mongo_client = MongoClient("mongodb+srv://kartik-2:8pc29aMnwZZSK7oI@drishyacluster.2beigid.mongodb.net/")
db = mongo_client["drishya"]
supervisor_collection = db["supervisor_info"]
site_collection = db["site_info"]
logo_collection = db["assets"]

def get_next_supervisor_id():
    # Function to get the next supervisor_id value
    last_supervisor = supervisor_collection.find_one(sort=[('supervisor_id', -1)])
    if last_supervisor is None:
        return 'sv_001'
    last_id = int(last_supervisor['supervisor_id'].split('_')[1])
    new_id = last_id + 1
    return f'sv_{str(new_id).zfill(3)}'

def get_site_names():
    # Function to get the names of all sites from site_info collection
    return [site['site_address'] for site in site_collection.find({})]

def get_site_id(site_name):
    # Function to get the site_id of the selected site from site_info collection
    site = site_collection.find_one({'site_address': site_name})
    return site['site_id']

def validate_name(name):
    # Function to check if name contains only alphabets (no digits) and spaces
    return all(char.isalpha() or char.isspace() for char in name)

def validate_contact_number(contact_number):
    # Function to check if contact_number has exactly 10 digits
    return contact_number.isdigit() and len(contact_number) == 10

def validate_aadhaar_number(aadhaar_number):
    # Function to check if aadhaar_number has exactly 12 digits
    return aadhaar_number.isdigit() and len(aadhaar_number) == 12

def validate_email(email):
    # Function to check if email ends with '@gmail.com'
    return email.lower().endswith('@gmail.com')

def add_supervisor(name, contact_number, aadhaar_number, date_of_birth, password, email, site_id, supervisor_id):
    # Convert date_of_birth to datetime.datetime
    date_of_birth = datetime.datetime.combine(date_of_birth, datetime.datetime.min.time())

    # Function to add supervisor to supervisor_info collection
    supervisor_data = {
        'name': name,
        'contact_number': contact_number,
        'aadhaar_number': aadhaar_number,
        'date_of_birth': date_of_birth,
        'password': password,
        'email': email, 
        'site_id': site_id,
        'supervisor_id': supervisor_id,
        'username': supervisor_id,
    }
    supervisor_collection.insert_one(supervisor_data)

def fetch_logo_image_from_mongodb():
    # Retrieve the logo image from MongoDB
    logo_data = logo_collection.find_one({"name": "Logo"})
    if logo_data:
        logo_image_bytes = logo_data["image"]
        return Image.open(io.BytesIO(logo_image_bytes))
    else:
        st.warning("Logo image not found in MongoDB.")
        return None

def main():
    # Fetch the logo image from MongoDB
    logo_image = fetch_logo_image_from_mongodb()

    if logo_image:
        # Resize the image to a larger size
        logo_image = logo_image.resize((300, 300))

        # Create a layout with two columns
        col1, col2 = st.columns([1, 3])

        # Display the logo image in the first column
        col1.image(logo_image, use_column_width=True, output_format='JPEG')

        # Display the title in the second column
        col2.header("Create Supervisor Account")

        name = st.text_input('Name')
        contact_number = st.text_input('Contact Number')
        aadhaar_number = st.text_input('Aadhaar Number')
        # Custom date range for date_of_birth (from 1940 to current date)
        min_date = datetime.date(1940, 1, 1)
        max_date = datetime.date.today()
        date_of_birth = st.date_input('Date of Birth', min_value=min_date, max_value=max_date)
        password = st.text_input('Password', type='password')
        email = st.text_input('Email ID')

        site_names = get_site_names()
        selected_site_name = st.selectbox('Select Site', site_names)
        site_id = get_site_id(selected_site_name)

        if st.button('Add Supervisor'):
            if not validate_name(name):
                st.error('Invalid name. Name should contain only alphabets (no digits).')
            elif not validate_contact_number(contact_number):
                st.error('Invalid contact number. Contact number must have exactly 10 digits.')
            elif not validate_aadhaar_number(aadhaar_number):
                st.error('Invalid Aadhaar number. Aadhaar number must have exactly 12 digits.')
            elif not validate_email(email):
                st.error('Invalid email. Email must end with "@gmail.com".')
            else:
                supervisor_id = get_next_supervisor_id()
                add_supervisor(name, contact_number, aadhaar_number, date_of_birth, password, email, site_id, supervisor_id)
                st.success(f'Supervisor added successfully! Supervisor Id : {supervisor_id} ')
    else:
        # If the logo image is not found, display a default heading
        st.markdown(
            f"""
            <div style='display: flex; justify-content: center;'>
                <h1 style='text-align: center;'>Welcome to Drishya</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
