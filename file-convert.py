import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="File Converter", layout="wide")
st.title("File Converter & Cleaner")
st.write("Upload CSV or Excel files, clean data, and convert format.")

# Add file uploader with accept_multiple_files=True
files = st.file_uploader("Upload CSV or Excel Files.", type=["csv", "xlsx"], accept_multiple_files=True, label_visibility='visible')

if files:
    for file in files:
        ext = file.name.split(".")[-1].lower()
        try:
            if ext == "csv":
                df = pd.read_csv(file)
            elif ext == "xlsx":
                df = pd.read_excel(file, engine='openpyxl')
            else:
                st.error(f"Unsupported file type: {ext}")
                continue
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")
            continue

        if not df.empty:
            st.subheader(f"{file.name} - Preview")
            st.dataframe(df.head())

            if st.checkbox(f"Remove Duplicates - {file.name}"):
                df = df.drop_duplicates()
                st.success("Duplicates Removed")
                st.dataframe(df.head())

            if st.checkbox(f"Fill Missing Values - {file.name}"):
                numeric_cols = df.select_dtypes(include=["number"]).columns
                if not numeric_cols.empty:
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("Missing Values Filled")
                    st.dataframe(df.head())
                else:
                    st.warning("No numeric columns to fill missing values.")

            selected_columns = st.multiselect(f"Select Columns - {file.name}", df.columns, default=list(df.columns))
            if selected_columns:
                df = df[selected_columns]
                st.dataframe(df.head())

            if st.checkbox(f"Show Chart - {file.name}") and not df.select_dtypes(include="number").empty:
                st.bar_chart(df.select_dtypes(include="number"))

            format_choice = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

            if st.button(f"Download {file.name} as {format_choice}"):
                output = io.BytesIO()
                if format_choice == "CSV":
                    df.to_csv(output, index=False)
                    mime = "text/csv"
                    new_name = file.name.replace(ext, "csv")
                else:
                    df.to_excel(output, index=False, engine='openpyxl')
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    new_name = file.name.replace(ext, "xlsx")

                output.seek(0)
                st.download_button(label=f"Download {new_name}", data=output, file_name=new_name, mime=mime)
                st.success("Processing Completed!")
        else:
            st.error("File is empty or could not be processed.")
