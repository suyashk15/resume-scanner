# Resume_Scanner

[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)

A simple keyword scanner for resumes

# Installation

1. Install Python (preferably, version >= 3.11)
2. To create a virtual env, open a terminal in the cloned repository folder and use the following commands

   ```sh
    python -m venv virtual-env
    ```
   ```sh
    cd .\virtual-env\Scripts\
    ```
   ```sh
    .\activate
    ```

3. Going back to the cloned folder, install all the requirements
    ```sh
    pip install -r .\requirements.txt
    ```

4. Run the streamlit app
    ```sh
    streamlit run resume_keyword_search.py
    ```

5. Start using `resume-scanner` :tada:


# Using Deployed Version

1. Open the app in your browser: https://god-resume-scanner.streamlit.app/

2. Upload the service account JSON file.

3. Upload the Excel spreadsheet with resume links.

4. Select the Resume Link column.
5. Enter keywords (comma-separated, e.g., Python, Django, Machine Learning, React).

6. Click the "Search Resumes" button.

7. The app will process resumes and display: Names of candidates whose resumes contain the keywords and links to their resumes.
