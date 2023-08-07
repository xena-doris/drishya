import streamlit as st
import pymongo
import subprocess
from PIL import Image
import io

# MongoDB Atlas connection
mongo_client = pymongo.MongoClient("mongodb+srv://kartik-2:8pc29aMnwZZSK7oI@drishyacluster.2beigid.mongodb.net/")
mongo_db = mongo_client['drishya']
collection = mongo_db['admin_info']
collection_logo = mongo_db['assets']

def fetch_logo_image_from_mongodb():
    # Retrieve the logo image from MongoDB Atlas
    logo_data = collection_logo.find_one({"name": "Logo"})
    if logo_data:
        logo_image_bytes = logo_data["image"]
        return Image.open(io.BytesIO(logo_image_bytes))
    else:
        st.warning("Logo image not found in MongoDB.")
        return None

def login_admin():
    admin_id = st.text_input("Enter your Admin ID:")
    password = st.text_input("Enter your password:", type="password")

    if st.button("Login"):
        try:
            # Retrieve the admin's credentials from MongoDB Atlas
            admin_data = collection.find_one({"admin_id": admin_id})
            if admin_data:
                db_admin_id = admin_data["admin_id"]
                db_password = admin_data["password"]
                if db_password == password:
                    st.success("Admin login successful. Welcome, Admin " + db_admin_id + "!")
                    # Additional actions or logic for the admin menu can be added here
                    redirect_to_admin_home()
                else:
                    st.error("Incorrect password. Please try again.")
            else:
                st.error("Invalid Admin ID. Please try again.")
        except pymongo.errors.PyMongoError as e:
            st.error("An error occurred: " + str(e))

def redirect_to_admin_home():
    subprocess.Popen(["streamlit", "run", "D:/adminghar.py"])

def main():
    # Fetch the logo image from MongoDB Atlas
    logo_image = fetch_logo_image_from_mongodb()

    if logo_image:
        # Resize the image to a larger size
        logo_image = logo_image.resize((300, 300))

        # Display the logo image with the custom heading
        st.markdown(
            f"""
            <div style='display: flex; flex-direction: column; align-items: center;'>
                <h1 style='text-align: center;'>Admin Login</h1>
                <img src='data:image/png;base64,{image_to_base64(logo_image)}' style='max-width: 300px; height: auto;'/>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Add a blank space for alignment
        st.write("")

        # Login as admin
        login_admin()
    else:
        st.warning("Logo image not found. Please check your MongoDB Atlas connection.")

def image_to_base64(image):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

if __name__ == "__main__":
    main()
