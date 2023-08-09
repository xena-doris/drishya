import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb+srv://****:*******@drishyacluster.2beigid.mongodb.net/')
db = client['drishya']
worker_info = db['worker_info']
supervisor_info = db['supervisor_info']
site_info = db['site_info']
worker_attendance = db['attendance']
supervisor_attendance = db['supervisor_attendance']

# Helper function to get attendance data for a specific date range
def get_attendance_data_date_range(start_date, end_date):
    start_date_iso = start_date.strftime('%Y-%m-%dT00:00:00.000Z')
    end_date_iso = end_date.strftime('%Y-%m-%dT23:59:59.999Z')

    # Retrieve all worker attendance data from MongoDB
    worker_attendance_data = worker_attendance.find({})
    worker_attendance_df = pd.DataFrame(list(worker_attendance_data))
    worker_attendance_df['punch_in'] = pd.to_datetime(worker_attendance_df['punch_in']).dt.strftime('%Y-%m-%dT00:00:00.000Z')

    # Filter the data based on the selected date range
    filtered_worker_attendance_df = worker_attendance_df[
        (worker_attendance_df['punch_in'] >= start_date_iso) & (worker_attendance_df['punch_in'] <= end_date_iso)
    ]

    return filtered_worker_attendance_df


# Helper function to get worker counts per site
def get_worker_counts_per_site():
    pipeline = [
        {
            '$group': {
                '_id': '$site_id',
                'worker_count': {'$sum': 1}
            }
        }
    ]
    result = worker_info.aggregate(pipeline)
    worker_counts = {str(res['_id']): res['worker_count'] for res in result}
    return worker_counts

# Helper function to get site address from site_id
def get_site_address(site_id):
    site = site_info.find_one({'site_id': site_id})
    return site['site_address'] if site else 'N/A'

# Helper function to count present and absent workers for each site on a specific date
def get_site_attendance_data(selected_site_ids, selected_date):
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    selected_date_iso = selected_date.strftime('%Y-%m-%dT00:00:00.000Z')
    site_attendance = worker_attendance.find({})

    if 'All' in selected_site_ids:
        df = pd.DataFrame(list(site_attendance))
        df['punch_in'] = pd.to_datetime(df['punch_in']).dt.strftime('%Y-%m-%dT00:00:00.000Z')

        present_count = df[df['punch_in'].str.startswith(selected_date_str)]['_id'].count()
        absent_count = total_workers - present_count
        return present_count, absent_count
    else:
        df = pd.DataFrame(list(site_attendance))
        df['punch_in'] = pd.to_datetime(df['punch_in']).dt.strftime('%Y-%m-%dT00:00:00.000Z')

        filtered_data = df[(df['site_id'].isin(selected_site_ids)) & (df['punch_in'].str.startswith(selected_date_str))]

        present_count = filtered_data['_id'].count()
        total_workers_selected_site = worker_info.count_documents({'site_id': {'$in': selected_site_ids}})
        absent_count = total_workers_selected_site - present_count
        return present_count, absent_count

# Load data for overall statistics
total_sites = site_info.count_documents({})
total_supervisors = supervisor_info.count_documents({})
total_workers = worker_info.count_documents({})

# Create the Streamlit app
def main():
    st.set_page_config(layout='wide')
    st.title('Attendance Dashboard')

    # Create a dictionary to map site_address to site_id
    site_id_to_address = {str(site['site_id']): site['site_address'] for site in site_info.find()}

    # Sidebar filters
    all_site_ids = list(site_id_to_address.keys())
    selected_site_ids = st.sidebar.multiselect('Select Sites', options=['All'] + all_site_ids, default=['All'], format_func=lambda x: 'All Sites' if x == 'All' else site_id_to_address[x])
    selected_date = st.sidebar.date_input('Select a Date for bar chart and supervisor attendance dataframe')
    # Line chart to display attendance trends over time
    start_date = st.sidebar.date_input('Select Start Date', value=datetime(2023, 1  , 1))
    end_date = st.sidebar.date_input('Select End Date', value=datetime(2023, 12, 31))

    # Overall statistics
    st.header('Overall Statistics')
    st.write(f'Total Sites: {total_sites}')
    st.write(f'Total Supervisors: {total_supervisors}')
    st.write(f'Total Workers: {total_workers}')


    # Create two layout columns for the first row (Stacked bar chart and Worker Counts per Site)
    col1, col2 = st.columns(2)
    with col1:
        # Stacked bar chart
        if selected_date and selected_site_ids:
            if 'All' in selected_site_ids:
                # Calculate attendance data for all sites and plot the stacked bar chart
                all_sites_present_counts = []
                all_sites_absent_counts = []
                site_addresses = list(site_id_to_address.values())

                for site_id in site_id_to_address.keys():
                    print(site_id)
                    present_count, absent_count = get_site_attendance_data([site_id], selected_date)
                    all_sites_present_counts.append(present_count)
                    all_sites_absent_counts.append(absent_count)

                fig = go.Figure(data=[
                    go.Bar(name='Present', x=site_addresses, y=all_sites_present_counts, text=all_sites_present_counts, textposition='auto'),
                    go.Bar(name='Absent', x=site_addresses, y=all_sites_absent_counts, text=all_sites_absent_counts, textposition='auto')
                ])

                fig.update_layout(title='Worker Attendance on Selected Date (All Sites)',
                                xaxis_title='Site',
                                yaxis_title='Number of Workers',
                                barmode='stack')

                st.header('Attendance on Selected Date (All Sites)')
                st.plotly_chart(fig,use_container_width=True)

            else:
                # Individual site selection
                site_addresses = [site_id_to_address[site_id] for site_id in selected_site_ids]
                present_counts = []
                absent_counts = []

                for site_id in selected_site_ids:
                    present_count, absent_count = get_site_attendance_data([site_id], selected_date)
                    present_counts.append(present_count)
                    absent_counts.append(absent_count)

                fig = go.Figure(data=[
                    go.Bar(name='Present', x=site_addresses, y=present_counts, text=present_counts, textposition='auto'),
                    go.Bar(name='Absent', x=site_addresses, y=absent_counts, text=absent_counts, textposition='auto')
                ])

                fig.update_layout(title='Worker Attendance on Selected Date',
                                xaxis_title='Site',
                                yaxis_title='Number of Workers',
                                barmode='stack')

                st.header('Attendance on Selected Date')
                st.plotly_chart(fig,use_container_width=True)

    with col2:
        # Add a pie chart to show worker counts per site
        st.header('Worker Counts per Site')
        worker_counts_per_site = get_worker_counts_per_site()
        if worker_counts_per_site:
            site_ids, worker_counts = zip(*worker_counts_per_site.items())
            site_addresses = [site_id_to_address[site_id] for site_id in site_ids]

            fig = go.Figure(data=[go.Pie(labels=site_addresses, values=worker_counts)])
            fig.update_layout(title='Number of Workers per Site')
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.write('No worker data available.')

    st.header('Attendance Trends over Time')
    if start_date <= end_date:
        df_worker= get_attendance_data_date_range(start_date, end_date)

        # Convert the punch_in column to datetime
        df_worker['punch_in'] = pd.to_datetime(df_worker['punch_in'])

        # Calculate total workers present on each date based on punch_in
        worker_counts_per_date = df_worker.groupby(df_worker['punch_in'].dt.date).size()

        fig_worker = go.Figure()
        fig_worker.add_trace(go.Scatter(x=worker_counts_per_date.index, y=worker_counts_per_date,
                                        mode='lines+markers', name='Worker Attendance'))
        fig_worker.update_layout(title='Worker Attendance Trends',
                                xaxis_title='Date',
                                yaxis_title='Attendance',
                                xaxis_tickformat='%Y-%m-%d',
                                yaxis_range=[13, 19])


        st.plotly_chart(fig_worker, use_container_width=True)
        
    else:
        st.error('Error: End Date must be after Start Date.')

if __name__ == '__main__':
    main()