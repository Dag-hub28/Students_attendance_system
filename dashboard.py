import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

def main():
    st.set_page_config(page_title="Attendance Dashboard", layout="wide")
    
    st.title("📊 Attendance Monitoring Dashboard")
    st.markdown("---")
    
    # Sidebar for controls
    st.sidebar.header("Controls")
    
    DATA_DIR = os.path.join('.', 'data')
    ATTENDANCE_DIR = os.path.join(DATA_DIR, 'attendance')
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)

    # Get available attendance files
    attendance_files = [f for f in os.listdir(ATTENDANCE_DIR) if f.startswith('attendance_') and f.endswith('.csv')]
    
    if not attendance_files:
        st.warning("No attendance records found. Run the attendance system first!")
        return
    
    # File selector
    selected_file = st.sidebar.selectbox(
        "Select Date",
        attendance_files,
        format_func=lambda x: x.replace('attendance_', '').replace('.csv', '')
    )
    
    # Read the selected file
    df = pd.read_csv(os.path.join(ATTENDANCE_DIR, selected_file))
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", len(df))
    with col2:
        st.metric("Earliest Arrival", df['Time'].min() if not df.empty else "N/A")
    with col3:
        st.metric("Latest Arrival", df['Time'].max() if not df.empty else "N/A")
    
    # Two columns for charts and table
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Attendance by Hour")
        # Convert time to hour
        df['Hour'] = pd.to_datetime(df['Time']).dt.hour
        hour_counts = df['Hour'].value_counts().sort_index()
        
        if not hour_counts.empty:
            fig = px.bar(x=hour_counts.index, y=hour_counts.values, 
                        labels={'x': 'Hour of Day', 'y': 'Number of Students'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Attendance Timeline")
        # Create timeline
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df_sorted = df.sort_values('DateTime')
        
        fig = px.scatter(df_sorted, x='DateTime', y='Name', 
                        title="Student Arrival Times")
        st.plotly_chart(fig, use_container_width=True)
    
    # Display the data table
    st.subheader("📋 Detailed Attendance Records")
    st.dataframe(
        df[['Name', 'Time', 'Date']].sort_values('Time'),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()