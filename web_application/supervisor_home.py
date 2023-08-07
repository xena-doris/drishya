import streamlit as st
import pymongo
import subprocess
from PIL import Image
import io

# MongoDB Atlas connection
mongo_client = pymongo.MongoClient("mongodb+srv://ritesh:ritesh123@drishyacluster.2beigid.mongodb.net/")
mongo_db = mongo_client['drishya']
collection_logo = mongo_db['assets']

def fetch_logo_image_from_mongodb():
    # Retrieve the logo image from MongoDB
    logo_data = collection_logo.find_one({"name": "Logo"})
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

        # Display the logo image with the custom heading "Supervisor Login"
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

        # Center-align the "Select Option" heading
        st.header("Choose Your Action")

        # Take Attendance button
        if st.button("Take Attendance", key="take_attendance", help="Click to take attendance"):
            # Action to perform when "Take Attendance" button is clicked
            st.write("You clicked on Take Attendance button!")
            # Redirect to the take_attendance page
            redirect_to_take_attendance()

        # Add Worker button
        if st.button("Add Worker", key="add_worker", help="Click to add a worker"):
            # Action to perform when "Add Worker" button is clicked
            st.write("You clicked on Add Worker button!")
            # Redirect to the add_worker page with supervisor ID
            redirect_to_add_worker()

        # View Workers button
        if st.button("View Workers", key="view_workers", help="Click to view workers"):
            # Action to perform when "View Workers" button is clicked
            st.write("You clicked on View Workers button!")
            # Redirect to the view_workers page
            redirect_to_view_worker()

        # Logout button
        if st.button("Logout", key="logout", help="Click to logout"):
            # Action to perform when "Logout" button is clicked
            st.write("You clicked on Logout button!")
            # Redirect to the login_homepage (D:/login_homepage)
            redirect_to_login_homepage()

    else:
        st.warning("Logo image not found. Please check your MongoDB.")

def image_to_base64(image):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def redirect_to_take_attendance():
    subprocess.Popen(["streamlit", "run", "D:/take_attendance.py"])


def redirect_to_add_worker():
    subprocess.Popen(["streamlit", "run", "D:/embeddings.py"], shell=True)


def redirect_to_view_worker():
    subprocess.Popen(["streamlit", "run", "D:/-board.py"])


def redirect_to_login_homepage():
    subprocess.Popen(["streamlit", "run", "D:/login_supervisor.py"])


if __name__ == "__main__":
    main()
