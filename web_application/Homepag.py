import streamlit as st
from PIL import Image
import pymongo
import io
import subprocess
import base64

# MongoDB Atlas connection
mongo_client = pymongo.MongoClient("mongodb+srv://ritesh:ritesh123@drishyacluster.2beigid.mongodb.net/")
db = mongo_client["drishya"]
collection_logo = db["assets"]

def main():
    # Fetch the logo image from MongoDB Atlas
    logo_image = fetch_logo_image_from_mongodb()

    if logo_image:
        # Resize the image to a larger size
        logo_image = logo_image.resize((300, 300))

        # Display the logo image with the custom heading
        st.markdown(
            f"""
            <div style='display: flex; justify-content: center;'>
                <h1 style='text-align: center;'>Welcome to Drishya</h1>
            </div>
            <div style='display: flex; justify-content: center;'>
                <img src='data:image/png;base64,{image_to_base64(logo_image)}' style='max-width: 300px; height: auto;'/>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Add a blank space for alignment
    st.write("")

    # Center-align the "Choose Your Action" heading
    st.header("Choose Your Action")

    # Create Admin Account button
    if st.button("Create Admin Account", key="create_admin", help="Click to create an Admin account"):
        # Action to perform when "Create Admin Account" button is clicked
        redirect_to_create_admin_page()

    # Increase the button size
    if st.button("Login as Supervisor", key="supervisor", help="Click to login as Supervisor"):
        # Action to perform when "Login as Supervisor" button is clicked
        redirect_to_login_supervisor()

    if st.button("Login as Admin", key="admin", help="Click to login as Admin"):
        # Action to perform when "Login as Admin" button is clicked
        redirect_to_login_admin()

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def fetch_logo_image_from_mongodb():
    # Retrieve the logo image from MongoDB Atlas
    logo_data = collection_logo.find_one({"name": "Logo"})
    if logo_data:
        logo_image_bytes = logo_data["image"]
        return Image.open(io.BytesIO(logo_image_bytes))
    else:
        st.warning("Logo image not found in MongoDB Atlas.")
        return None

def redirect_to_create_admin_page():
    subprocess.Popen(["streamlit", "run", "D:/create_admin4.py"])

def redirect_to_login_admin():
    subprocess.Popen(["streamlit", "run", "D:/admin_login3.py"])

def redirect_to_login_supervisor():
    subprocess.Popen(["streamlit", "run", "D:/login_supervisor.py"])

if __name__ == "__main__":
    main()
