import streamlit as st
import pymongo
from PIL import Image
import subprocess
import io

# MongoDB Atlas connection
mongo_client = pymongo.MongoClient("mongodb+srv://ritesh:ritesh123@drishyacluster.2beigid.mongodb.net/")
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
        st.warning("Logo image not found in MongoDB Atlas.")
        return None

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
                <h1 style='text-align: center;'>Admin Homepage</h1>
            </div>
            <div style='display: flex; justify-content: center;'>
                <img src='data:image/png;base64,{image_to_base64(logo_image)}' style='max-width: 300px; height: auto;'/>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Add a blank space for alignment
        st.write("")

        # Center-align the "Choose User Type" heading
        st.header("Choose Your Action")

        # Add Supervisor button
        if st.button("Add Supervisor", key="add_supervisor", help="Click to add a supervisor"):
            # Action to perform when "Add Supervisor" button is clicked
            st.write("You clicked on Add Supervisor button!")
            # Redirect to a new web page
            redirect_to_add_supervisor()

        # Add Site button
        if st.button("Add Site", key="add_site", help="Click to add a site"):
            # Action to perform when "Add Site" button is clicked
            st.write("You clicked on Add Site button!")
            # Redirect to a new web page
            redirect_to_add_site()

        # See Dashboard button
        if st.button("See Dashboard", key="see_dashboard", help="Click to see the dashboard"):
            # Action to perform when "See Dashboard" button is clicked
            st.write("You clicked on See Dashboard button!")
            # Redirect to a new web page
            redirect_to_dashboard()

        # Go Back button
        if st.button("Go Back", key="go_back", help="Click to go back"):
            # Action to perform when "Go Back" button is clicked
            st.write("You clicked on Go Back button!")
            # Redirect to the previous page
            redirect_to_home_page()
    else:
        st.warning("Logo image not found. Please check your MongoDB Atlas connection.")

def image_to_base64(image):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def redirect_to_add_supervisor():
    subprocess.Popen(["streamlit", "run", "D:/add_supervisor.py"])

def redirect_to_add_site():
    subprocess.Popen(["streamlit", "run", "D:/add_site.py"])

def redirect_to_dashboard():
    subprocess.Popen(["streamlit", "run", "D:/-board.py"])

def redirect_to_home_page():
    subprocess.Popen(["streamlit", "run", "D:/Homepage.py"])

if __name__ == "__main__":
    main()
