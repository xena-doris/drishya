import streamlit as st
import cv2
import numpy as np
import face_recognition
import pymongo
from PIL import Image
import io

atlas_connection_string = "mongodb+srv://ritesh:ritesh123@drishyacluster.2beigid.mongodb.net/"
# Establish a connection to MongoDB Atlas
client = pymongo.MongoClient(atlas_connection_string)
db = client["drishya"]
collection = db["worker_info"]
logo_collection = db["assets"]

# Function to fetch the logo image from the database
def fetch_logo_image_from_mongodb():
    # Retrieve the logo image from MongoDB
    logo_data = logo_collection.find_one({"name": "Logo"})
    if logo_data:
        logo_image_bytes = logo_data["image"]
        return Image.open(io.BytesIO(logo_image_bytes))
    else:
        st.warning("Logo image not found in MongoDB.")
        return None

# Function to get the last assigned worker_id from the database
def get_last_worker_id():
    last_document = collection.find_one({}, sort=[("worker_id", pymongo.DESCENDING)])
    if last_document:
        last_worker_id = int(last_document["worker_id"].split("_")[1])
    else:
        last_worker_id = 0
    return last_worker_id

# Function to generate the next worker_id in "w_000" format
def generate_next_worker_id():
    last_worker_id = get_last_worker_id()
    next_worker_id = last_worker_id + 1
    return f"w_{str(next_worker_id).zfill(3)}"

# Function to capture an image, detect face, and create embeddings
def capture_and_store_embedding(person_name, address, mobile_no, dob, adhar_card_no, site_id, supervisor_id):
    # Open the camera
    cap = cv2.VideoCapture(0)

    # Capture a single frame
    ret, frame = cap.read()

    if not ret:
        st.error("Unable to capture frame.")
        return

    # Release the camera
    cap.release()

    # Display the frame with rectangles
    face_locations = face_recognition.face_locations(frame)
    for top, right, bottom, left in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Show the frame in a Streamlit window
    st.image(frame, channels="BGR", use_column_width=True)

    if len(face_locations) == 0:
        st.error("No face found in the captured image.")
    else:
        # Convert the frame to RGB format (required by face_recognition library)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Compute the face embeddings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(face_encodings) == 0:
            st.error("No face found in the captured image.")
        else:
            # Create a data dictionary to store in MongoDB
            worker_id = generate_next_worker_id()
            data = {
                "worker_id": worker_id,
                "name": person_name,
                "address": address,
                "mobile_no": mobile_no,
                "date_of_birth": dob,
                "aadhar_card_no": adhar_card_no,
                "site_id": site_id,
                "supervisor_id": supervisor_id,
                "embeddings": face_encodings[0].tolist()
            }

            # Insert the data into the MongoDB collection
            collection.insert_one(data)

            # Print the data
            st.success(f"Data and embeddings saved successfully for {person_name}.")

# Create the Streamlit app
def main():
    # Fetch the logo image from MongoDB
    logo_image = fetch_logo_image_from_mongodb()

    if logo_image:
        # Resize the image to a smaller size
        logo_image = logo_image.resize((150, 150))

        # Create a layout with two columns
        col1, col2 = st.columns([1, 3])

        # Display the logo image in the first column
        col1.image(logo_image, use_column_width=False)

        # Display the title "Face Recognition Data and Worker Details" in the second column
        col2.title("Face Recognition Data and Worker Details")

    # Get person details using Streamlit widgets
    person_name = st.text_input("Enter the person's name:")
    address = st.text_input("Address:")
    mobile_no = st.text_input("Mobile No:")
    dob = st.text_input("Date of Birth:")
    adhar_card_no = st.text_input("Aadhar Card No:")
    site_id = st.text_input("Site ID:")
    supervisor_id = st.text_input("Supervisor ID:")

    # Capture button to capture an image
    if st.button("Capture"):
        if not person_name or not address or not mobile_no or not dob or not adhar_card_no or not site_id or not supervisor_id:
            st.error("Please fill in all the details before capturing.")
        else:
            capture_and_store_embedding(person_name, address, mobile_no, dob, adhar_card_no, site_id, supervisor_id)

if __name__ == "__main__":
    main()