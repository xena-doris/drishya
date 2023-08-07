import streamlit as st
from pymongo import MongoClient
from PIL import Image
import io

# Connect to MongoDB
client = MongoClient('mongodb+srv://kartik-2:8pc29aMnwZZSK7oI@drishyacluster.2beigid.mongodb.net/')
db = client['drishya']
site_collection = db['site_info']
logo_collection = db['assets']

def get_next_site_id():
    # Function to get the next site_id value
    last_site = site_collection.find_one(sort=[('site_id', -1)])
    if last_site is None:
        return 'si_001'
    last_id = int(last_site['site_id'].split('_')[1])
    new_id = last_id + 1
    return f'si_{str(new_id).zfill(3)}'

def add_site(site_address, site_id):
    # Function to add site to site_info collection
    site_data = {
        'site_id': site_id,
        'site_address': site_address,
    }
    site_collection.insert_one(site_data)

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
        col1.image(logo_image, use_column_width=True)

        # Display the title "Add Site" in the second column
        col2.title('Add Site')

    site_address = st.text_input('Site Address')

    if st.button('Add Site'):
        site_id = get_next_site_id()
        add_site(site_address, site_id)
        st.success(f'Site added successfully! Site Id : {site_id}')

if __name__ == '__main__':
    main()
