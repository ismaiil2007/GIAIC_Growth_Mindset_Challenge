#Live Link: https://data-sweeper-and-convertor-by-ismail-hussain.streamlit.app/

import streamlit as st
import pandas as pd 
import os
from io import BytesIO


st.set_page_config(page_title="Data sweeper and Analyzer", page_icon="📉" , layout="wide", initial_sidebar_state="expanded")
st.title('Data sweeper and Analyzer')
st.subheader('Convert your files from CSV and Excel formats with Built-in data cleaning and Visualisation')

# Initialize session state for dataframes if not exists
if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}

# Helper function to show data preview with full data option
def show_data_preview(df, section_name, i, file):
    show_full = st.checkbox(f'Show Full Dataset for {section_name}', key=f"show_full_{section_name}_{i}_{file.name}")
    if show_full:
        st.dataframe(df)
        st.write(f'Total Rows: {len(df)}, Total Columns: {len(df.columns)}')
    else:
        st.write('First Five rows of Data:')
        st.dataframe(df.head())

# Helper function to show result preview
def show_result_preview(df, operation_name, i, file):
    st.write(f"Result after {operation_name}:")
    show_full = st.checkbox('Show Full Document', key=f"show_result_{operation_name}_{i}_{file.name}")
    if show_full:
        st.dataframe(df)
    else:
        st.dataframe(df.head())
    st.write(f'Total Rows: {len(df)}, Total Columns: {len(df.columns)}')

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
        
        # Initial Data preview
        st.write('Data Preview:')
        show_data_preview(df, "initial", i, file)

        st.subheader('Data Cleaning Options:')

        if st.checkbox("Clean Data for: " + file.name, key=f"clean_{i}_{file.name}"):
            # Option 1: Remove Duplicate Rows
            st.write("1. Remove Duplicate Rows")
            if st.button('Remove Duplicate Rows from ' + file.name, key=f"dup_rows_{i}_{file.name}"):
                initial_rows = len(df)
                df.drop_duplicates(inplace=True)
                removed_rows = initial_rows - len(df)
                st.success(f'Removed {removed_rows} duplicate rows successfully')
                if removed_rows > 0:
                    show_result_preview(df, "removing_duplicate_rows", i, file)
            
            st.markdown("---")  # Separator line
            
            # Option 2: Remove Duplicate Columns
            st.write("2. Remove Duplicate Columns")
            if st.button('Remove Duplicate Columns from ' + file.name, key=f"dup_cols_{i}_{file.name}"):
                initial_cols = len(df.columns)
                # Find duplicate columns
                duplicate_cols = {}
                for col1 in df.columns:
                    for col2 in df.columns:
                        if col1 != col2 and col1 not in sum(duplicate_cols.values(), []):
                            if df[col1].equals(df[col2]):
                                if col1 in duplicate_cols:
                                    duplicate_cols[col1].append(col2)
                                else:
                                    duplicate_cols[col1] = [col2]
                
                # Remove duplicate columns but keep one instance
                cols_to_remove = sum(duplicate_cols.values(), [])
                if cols_to_remove:
                    df.drop(columns=cols_to_remove, inplace=True)
                    st.success('Duplicate columns removed successfully')
                    st.write('Kept columns:', list(duplicate_cols.keys()))
                    st.write('Removed duplicate columns:', cols_to_remove)
                    show_result_preview(df, "removing_duplicate_columns", i, file)
                else:
                    st.info('No duplicate columns found')
            
            st.markdown("---")  # Separator line
            
            # Option 3: Fill Missing Values
            st.write("3. Fill Missing Values")
            if st.button('Fill missing values for ' + file.name, key=f"fill_{i}_{file.name}"):
                numeric_cols = df.select_dtypes(include=["number"]).columns
                if len(numeric_cols) > 0:
                    initial_nulls = df[numeric_cols].isnull().sum().sum()
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success(f'Filled {initial_nulls} missing values successfully')
                    if initial_nulls > 0:
                        show_result_preview(df, "filling_missing_values", i, file)
                else:
                    st.info('No numeric columns found to fill missing values')
            
            st.markdown("---")  # Separator line
            
            # Option 4: Remove Rows by Value
            st.write("4. Remove Rows by Value")
            selected_column = st.selectbox(
                "Select column",
                df.columns,
                key=f"sel_col_{i}_{file.name}"
            )
            
            if selected_column:
                unique_values = df[selected_column].unique()
                selected_value = st.selectbox(
                    f"Select value from {selected_column}",
                    unique_values,
                    key=f"sel_val_{i}_{file.name}"
                )
                
                if selected_value:
                    matching_rows = df[df[selected_column] == selected_value]
                    st.write(f"Found {len(matching_rows)} rows where {selected_column} = {selected_value}")
                    
                    st.write("Matching rows:")
                    show_data_preview(matching_rows, "matching_rows", i, file)
                    
                    row_indices = matching_rows.index.tolist()
                    rows_to_keep = st.multiselect(
                        "Select rows to keep (unselected rows will be removed)",
                        row_indices,
                        format_func=lambda x: f"Row {x}: {dict(matching_rows.loc[x])}",
                        key=f"keep_rows_{i}_{file.name}"
                    )
                    
                    # Create a container for the result
                    result_container = st.container()
                    
                    if st.button('Remove Selected Rows', key=f"remove_rows_{i}_{file.name}"):
                        rows_to_remove = list(set(row_indices) - set(rows_to_keep))
                        if rows_to_remove:
                            df.drop(rows_to_remove, inplace=True)
                            st.success(f"Removed {len(rows_to_remove)} rows")
                            
                            # Display results in the container
                            with result_container:
                                st.write("Result after removing selected rows:")
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    show_full = st.checkbox('Show Full Document', key=f"show_full_after_remove_{i}_{file.name}")
                                with col2:
                                    if show_full:
                                        st.dataframe(df)
                                    else:
                                        st.dataframe(df.head())
                                st.write(f'Total Rows: {len(df)}, Total Columns: {len(df.columns)}')
                        else:
                            st.info("No rows were selected for removal")

            st.markdown("---")  # Separator line

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
                    
                    
