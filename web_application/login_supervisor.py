import streamlit as st
import pymongo
import subprocess
import base64
from PIL import Image
import io

# MongoDB Atlas connection
mongo_client = pymongo.MongoClient("mongodb+srv://ritesh:ritesh123@drishyacluster.2beigid.mongodb.net/")
mongo_db = mongo_client['drishya']
collection = mongo_db['supervisor_info']
collection_logo = mongo_db['assets']

def fetch_logo_image_from_mongodb():
    # Retrieve the logo image from MongoDB Atlas
    logo_data = collection_logo.find_one({"name": "Logo"})
    if logo_data:
        logo_image_bytes = logo_data["image"]
        return Image.open(io.BytesIO(logo_image_bytes))
    else:
        st.warning("Logo image not found in MongoDB Atlas.")
        return None

def login_supervisor():
    supervisor_id = st.text_input("Enter your Supervisor ID:")
    password = st.text_input("Enter your password:", type="password")

    if st.button("Login"):
        try:
            # Retrieve the supervisor's credentials from MongoDB Atlas
            supervisor_data = collection.find_one({"supervisor_id": supervisor_id})
            if supervisor_data:
                db_supervisor_id = supervisor_data["supervisor_id"]
                db_password = supervisor_data["password"]
                if db_password == password:
                    st.success("Supervisor login successful. Welcome, " + db_supervisor_id + "!")
                    # Additional actions or logic for the supervisor menu can be added here
                    redirect_to_supervisor_home()
                else:
                    st.error("Incorrect password. Please try again.")
            else:
                st.error("Invalid Supervisor ID. Please try again.")
        except pymongo.errors.PyMongoError as e:
            st.error("An error occurred: " + str(e))

def redirect_to_supervisor_home():
    subprocess.Popen(["streamlit", "run", "D:/supervisor_home.py"])

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
                <h1 style='text-align: center;'>Supervisor Login</h1>
            </div>
            <div style='display: flex; justify-content: center;'>
                <img src='data:image/png;base64,{image_to_base64(logo_image)}' style='max-width: 300px; height: auto;'/>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Add a blank space for alignment
        st.write("")

        # Login as supervisor
        login_supervisor()
    else:
        st.warning("Logo image not found. Please check your MongoDB Atlas connection.")

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

if __name__ == "__main__":
    main()
