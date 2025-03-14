

import streamlit as st
import pandas as pd 
import os
from io import BytesIO


st.set_page_config(page_title="Data sweeper and Analyzer", page_icon="📉" , layout="wide", initial_sidebar_state="expanded")
st.title('Data sweeper and Analyzer')
st.subheader('Convert your files from CSV and Excel formats with Built-in data cleaning and Visualisation')

uploaded_files = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'], accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == '.csv':
            df = pd.read_csv(file)
        elif file_ext == '.xlsx':
            df = pd.read_excel(file)
        else: 
            st.error("Please upload a CSV or Excel file: " + file_ext)
            st.stop()
            continue

        st.subheader(file.name)
        st.write('File uploaded successfully: ' + file.name)
        st.write("File Size: ", file.size/1024)
        st.write('First Five rows of Data:')
        st.dataframe(df.head())

        st.subheader('Data Cleaning Options:')

        if st.checkbox("Clean Data for: " + file.name, key=f"clean_{i}_{file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button('Remove Duplicates from ' + file.name, key=f"dup_{i}_{file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write('Duplicates removed successfully')
            
            with col2:
                if st.button('Fill missing values for ' + file.name, key=f"fill_{i}_{file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write('Missing values filled successfully')

        st.subheader("Select columns in " + file.name + " to Convert")
        columns = st.multiselect("Select columns to convert", df.columns, default=df.columns, key=f"cols_{i}_{file.name}")
        df = df[columns]

        st.subheader("Data Visualization")
        if st.checkbox('Show Visualization for: ' + file.name, key=f"viz_{i}_{file.name}"):
            st.bar_chart(df.select_dtypes(include=["number"]).iloc[:,:3])

        st.subheader("Conversion Options")
        conversion_types = st.radio('Convert ' + file.name + ' to:', ['CSV', 'Excel'], key=f"conv_{i}_{file.name}")
        if st.button('Convert: ' + file.name, key=f"btn_{i}_{file.name}"):
            buffer = BytesIO()
            if conversion_types == 'CSV':
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = 'text/csv'
            elif conversion_types == 'Excel':
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            buffer.seek(0)

            st.download_button(
                label='⬇ Download ' + file.name + " as " + conversion_types, 
                data=buffer, 
                file_name=file_name, 
                mime=mime_type,
                key=f"download_{i}_{file.name}"
            )
                    
                    
