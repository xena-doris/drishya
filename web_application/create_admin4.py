import streamlit as st
from PIL import Image
import pymongo
import io
import base64
import re
from datetime import date

# MongoDB connection
mongo_client = pymongo.MongoClient("mongodb+srv://kartik-2:8pc29aMnwZZSK7oI@drishyacluster.2beigid.mongodb.net/")
mongo_db = mongo_client["drishya"]
collection = mongo_db["admin_info"]
collection_logo = mongo_db["assets"]
admin_counter_collection = mongo_db["admin_counter"]

# Function to fetch the logo image from the database
def fetch_logo_image_from_mongodb():
    # Retrieve the logo image from MongoDB
    logo_data = collection_logo.find_one({"name": "Logo"})
    if logo_data:
        logo_image_bytes = logo_data["image"]
        return Image.open(io.BytesIO(logo_image_bytes))
    else:
        st.warning("Logo image not found in MongoDB.")
        return None

def validate_name(name):
    if any(char.isdigit() for char in name):
        return False
    return True

def validate_email(email):
    # Check if email ends with '@gmail.com'
    if not email.lower().endswith('@gmail.com'):
        return False
    return True

def validate_date_of_birth(date_of_birth):
    # Using regex pattern to validate date format (YYYY-MM-DD)
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_of_birth):
        return False
    return True

def validate_aadhaar_number(aadhaar_number):
    if len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
        return False
    return True

# Function to validate contact number (10 digits)
def validate_contact_number(contact_number):
    # Remove leading and trailing whitespaces from the input
    contact_number = contact_number.strip()

    if len(contact_number) != 10 or not contact_number.isdigit():
        return False
    return True

def get_next_admin_id():
    # Function to get the next admin_id value
    last_admin = collection.find_one(sort=[('admin_id', -1)])
    if last_admin is None:
        return 'ai_001'
    last_id = int(last_admin['admin_id'].split('_')[1])
    new_id = last_id + 1
    return f'ai_{str(new_id).zfill(3)}'

def create_admin():
    # Get the next admin ID
    admin_id = get_next_admin_id()

    # Get user inputs for admin details
    name = st.text_input("Enter your name (no digits allowed): ", key="admin_name")
    contact_number = st.text_input("Enter your contact number (10 digits): ", key="admin_contact")
    email_id = st.text_input("Enter your email ID (ending with '@gmail.com'): ", key="admin_email")
    aadhaar_number = st.text_input("Enter your Aadhaar number (12 digits): ", key="admin_aadhaar")
    
    # Use streamlit.date_input() to get the date of birth
    min_date = date(1900, 1, 1)  # Set the minimum allowed date
    max_date = date(2100, 12, 31)  # Set the maximum allowed date
    date_of_birth = st.date_input("Enter your date of birth:", key="admin_dob", min_value=min_date, max_value=max_date)

    username = st.text_input("Enter a username: ", key="admin_username")
    password = st.text_input("Enter a password: ", type="password", key="admin_password")

    if st.button("Submit", key="admin_submit"):
        if not validate_name(name):
            st.error("Invalid name. Name must not have any digits.")
        elif not validate_contact_number(contact_number):
            st.error("Invalid contact number. Contact number must have 10 digits.")
        elif not validate_email(email_id):
            st.error("Invalid email ID. Email ID must end with '@gmail.com'.")
        elif not validate_aadhaar_number(aadhaar_number):
            st.error("Invalid Aadhaar number. Aadhaar number must have 12 digits.")
        elif not validate_date_of_birth(date_of_birth.strftime("%Y-%m-%d")):
            st.error("Invalid date of birth. Date must be in the format YYYY-MM-DD.")
        else:
            try:
                # Check if the username already exists
                if collection.find_one({"username": username}):
                    st.error("Username already exists. Please choose a different username.")
                else:
                    # Create a new admin account
                    admin_data = {
                        'admin_id': admin_id,
                        'username': username,
                        'password': password,
                        'name': name,
                        'contact_number': contact_number,
                        'email_id': email_id,
                        'aadhaar_number': aadhaar_number,
                        'date_of_birth': date_of_birth.strftime("%Y-%m-%d")
                    }
                    collection.insert_one(admin_data)
                    st.success("Admin account created successfully. Admin ID: " + admin_id)
            except pymongo.errors.PyMongoError as e:
                st.error("An error occurred: " + str(e))

def main():
    # Fetch the logo image from MongoDB
    logo_image = fetch_logo_image_from_mongodb()

    if logo_image:
        # Resize the image to a larger size
        logo_image = logo_image.resize((300, 300))

        # Create a layout with two columns
        col1, col2 = st.columns([1, 3])

        # Display the logo image in the first column
        col1.image(logo_image, use_column_width=True)

        # Display the title "Create Admin Account" in the second column
        col2.header("Create Admin Account")

    create_admin()

if __name__ == "__main__":
    main()
