import streamlit as st
import pandas as pd
import PyPDF2
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import io
import json
import re

def extract_file_id(drive_link):
    """
    Extract Google Drive file ID from a given link.
    Supports multiple link formats.
    """
    patterns = [
        r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",  # Standard link
        r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)",  # Open link
        r"drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)"    # Export/download link
    ]

    for pattern in patterns:
        match = re.search(pattern, drive_link)
        if match:
            return match.group(1)
    return None

# Function to initialize Google Drive API service
@st.cache_resource
def get_drive_service(credentials_file):
    try:
        scopes = ["https://www.googleapis.com/auth/drive.readonly"]
        creds = Credentials.from_service_account_info(json.load(credentials_file), scopes=scopes)
        service = build("drive", "v3", credentials=creds)
        # st.success("Google Drive API service initialized successfully!")
        return service
    except Exception as e:
        st.error(f"Failed to initialize Google Drive API: {e}")
        return None

# Function to extract text from Google Drive PDF
def extract_text_from_drive_pdf(service, file_id):
    try:
        request = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        file_stream.seek(0)

        # Extract text
        text = ""
        reader = PyPDF2.PdfReader(file_stream)
        for page in reader.pages:
            text += page.extract_text() if page.extract_text() else ''
        return text
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# Streamlit App UI
def main():
    st.title("🔍 Resume Keyword Search Tool")

    # Input credentials file
    credentials_file = st.file_uploader("Upload Google Service Account Credentials (JSON)", type="json")

    if credentials_file:
        st.success("Credentials file uploaded successfully!")
        st.write("File Name:", credentials_file.name)
        drive_service = get_drive_service(credentials_file)
        # if drive_service:
        #     st.success("Google Drive API service is working!")
        if not drive_service:
            st.error("Google Drive service initialization failed.")

        # Upload the spreadsheet
        spreadsheet = st.file_uploader("Upload Candidate Spreadsheet (Excel)", type=["xlsx"])
        if spreadsheet:
            st.success("Candidate Spreadsheet uploaded successfully!")
            df = pd.read_excel(spreadsheet)
            st.write("### Preview of Spreadsheet:")
            st.dataframe(df)

            # Select column for resume links
            resume_column = st.selectbox("Select the column with resume links:", df.columns)

            # Enter keywords to search
            keywords = st.text_area("Enter keywords (comma-separated)").split(",")
            keywords = [k.strip() for k in keywords if k.strip()]

            # Process resumes
            if st.button("Search Resumes"):
                if not keywords:
                    st.warning("Please enter at least one keyword.")
                    return

                matching_resumes = []

                with st.spinner("Processing resumes..."):
                    for index, row in df.iterrows():
                        drive_link = row[resume_column]
                        candidate_name = row.get("Name", f"Candidate_{index}")

                        # Extract File ID from Google Drive Link
                        try:
                            file_id = extract_file_id(drive_link)
                        except IndexError:
                            st.warning(f"Invalid drive link for {candidate_name}")
                            continue

                        # Extract PDF text
                        text = extract_text_from_drive_pdf(drive_service, file_id)
                        if text and any(keyword.lower() in text.lower() for keyword in keywords):
                            matching_resumes.append({"Name": candidate_name, "Resume Link": drive_link})
                            st.success(f"Keyword(s) found in resume of: {candidate_name}")

                # Display Results
                if matching_resumes:
                    st.write("### Resumes containing the keywords:")

                    table_md = "| Candidate Name | Resume Link |\n|---|---|\n"

                    for match in matching_resumes:
                        name = match['Name']
                        link = match['Resume Link']
                        table_md += f"| {name} | [Resume Link]({link}) |\n"

                    # Render the table as Markdown
                    st.markdown(table_md, unsafe_allow_html=True)
                else:
                    st.info("No resumes matched the given keywords.")

if __name__ == "__main__":
    main()
