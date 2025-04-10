# TVOTFC-Web-Application

## Setup Instructions

Note: Python will need to be previously installed.

Follow these steps to set up the project:

1. Clone the repository
    ```sh
    git clone <repo>
    cd TVOTFC-Web-Application
    ```

2. Create and activate a virtual environment
    ```sh
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies
    ```sh
    pip install -r requirements.txt
    ```

4. Set up Flask environment
    ```sh
    # Windows
    $env:FLASK_APP = "main.py"

    # Linux/macOS
    export FLASK_APP=main.py
    ```

5. Initialize the database
    ```sh
    flask db upgrade
    ```

6. Run the application
    ```sh
    flask run
    ```

The application will be available at `http://127.0.0.1:5000`

## Database Management

### Empty the Database
To empty all tables in the database (this will remove all participants, categories, and scores):
```sh
flask empty-db
```

### Modify Database Structure
If you need to make changes to the database structure:

1. Modify the models in `models/tables.py`

2. Generate a new migration
    ```sh
    flask db migrate -m "Description of your changes"
    ```

3. Review the generated migration in `migrations/versions/`

4. Apply the migration
    ```sh
    flask db upgrade
    ```

To revert a migration:
```sh
flask db downgrade
```

## File Upload Formats

The application supports uploading participant data in both CSV and Excel formats:

### Supported File Types
- CSV files (.csv)
- Excel files (.xlsx, .xls)

### Supported Column Names
The following column name variations are accepted (case-insensitive):

- First Name:
  - "First Name"
  - "Name (First Name)"
  - "FirstName" (with or without space)
  - "First_Name"

- Last Name:
  - "Last Name"
  - "Name (Last Name)"
  - "LastName" (with or without space)
  - "Last_Name"

- Age:
  - "Age"
  - "age"

- City:
  - "City"
  - "Address (City)"
  - "city"

- State:
  - "State"
  - "Address (State)"
  - "state"

Note: The system will recognize these column names regardless of spaces or letter case (e.g., "FirstName", "First Name", "firstname" are all valid).