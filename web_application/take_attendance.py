import numpy as np
import face_recognition
import pymongo
from bson.objectid import ObjectId
from io import BytesIO
import cv2
import streamlit as st
from datetime import datetime

# Replace the connection string with your MongoDB Atlas connection string for the "drishya" database
connection_string = "mongodb+srv://ritesh:ritesh123@drishyacluster.2beigid.mongodb.net/"

try:
    # Attempt to establish the connection to MongoDB
    client = pymongo.MongoClient(connection_string)
    db = client["drishya"]
    worker_info_collection = db["worker_info"]
    attendance_collection = db["attendance"]  # New collection for storing attendance

except Exception as e:
    # Connection failed, print the error message
    st.error(f"Error: MongoDB connection failed. {e}")
    exit()

# Load the stored embeddings and details from MongoDB for face recognition
def load_data():
    data = {}
    for person_data in worker_info_collection.find():
        person_name = person_data["name"]
        embedding = np.array(person_data["embeddings"], dtype=np.float64)
        data[person_name] = {"embedding": embedding, "details": person_data}

    return data

# Calculate the Euclidean distance between two face encodings
def euclidean_distance(face_encoding1, face_encoding2):
    return np.linalg.norm(face_encoding1 - face_encoding2)

# Recognize faces using the loaded embeddings
def recognize_face(data, frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    recognized_persons = []

    for face_encoding in face_encodings:
        min_distance = float("inf")
        recognized_person = None
        for person_name, person_data in data.items():
            stored_embedding = person_data['embedding']
            distance = euclidean_distance(stored_embedding, face_encoding)

            # Set a suitable threshold for face recognition (lower value for higher accuracy)
            if distance < 0.5:
                min_distance = distance
                recognized_person = person_name

        if recognized_person:
            recognized_persons.append(recognized_person)
        else:
            recognized_persons.append("Unknown Person")

    return recognized_persons, face_locations

def display_message(is_recognized, person_name, details):
    message = ""  # Initialize the message variable

    if is_recognized:
        # Get the current date and time
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if the person's name already exists in the attendance data for today
        today = datetime.now().strftime('%Y-%m-%d')
        attendance_record = attendance_collection.find_one({"Name": person_name, "Date": today})

        if attendance_record:
            # If the person has already punched out, do not update the Punch Out time again
            if "Punch Out" in attendance_record and not attendance_record["Punch Out"]:
                attendance_collection.update_one(
                    {"_id": attendance_record["_id"]},
                    {"$set": {"Punch Out": timestamp}}
                )
                message = f"Punch Out recorded for {person_name}."
            elif "Punch In" in attendance_record and not attendance_record["Punch In"]:
                # If the person has already punched in, do not update the Punch In time again
                attendance_collection.update_one(
                    {"_id": attendance_record["_id"]},
                    {"$set": {"Punch In": timestamp}}
                )
                message = f"Punch In recorded for {person_name}."
            else:
                # If neither Punch In nor Punch Out time is set, mark it as Punch In
                attendance_collection.update_one(
                    {"_id": attendance_record["_id"]},
                    {"$set": {"Punch In": timestamp}}
                )
                message = f"Punch In recorded for {person_name}."
        else:
            # If the person is new, create a new record for Punch In
            attendance_record = {
                "Name": person_name,
                "Date": today,
                "Punch In": timestamp,
                "Punch Out": "",
                "Worker ID": details.get("worker_id", ""),
                "Supervisor ID": details.get("supervisor_id", ""),
                "Site ID": details.get("site_id", "")
            }
            attendance_collection.insert_one(attendance_record)
            message = f"Punch In recorded for {person_name}."

    else:
        message = "Unknown person detected."

    st.info(message)

def face_recognition_main():
    # Load the data (embeddings and details) from MongoDB
    data = load_data()

    st.title("Take Attendance")

    # Open the camera
    cap = cv2.VideoCapture(0)

    if st.button("Recognize"):
        ret, frame = cap.read()

        if ret:
            # Convert BGR frame to RGB for face_recognition library
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Recognize faces in the current frame
            recognized_persons, face_locations = recognize_face(data, rgb_frame)

            # Display the names of recognized persons in real-time
            for (top, right, bottom, left), person_name in zip(face_locations, recognized_persons):
                color = (0, 255, 0) if person_name != "Unknown Person" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, person_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Convert the frame to RGB format for displaying with Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Display the frame using Streamlit
            st.image(frame_rgb, channels="RGB", use_column_width=True)

            # Handle attendance recording and display message
            if recognized_persons and recognized_persons[0] != "Unknown Person":
                person_name = recognized_persons[0]
                details = data[person_name]["details"]
                display_message(True, person_name, details)
            else:
                display_message(False, "")

    # Release the capture and close the OpenCV windows
    cap.release()

if __name__ == '__main__':
    face_recognition_main()
