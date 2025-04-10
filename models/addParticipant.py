from flask import Blueprint, render_template, request, redirect
from models import db
from models.tables import Participant
import csv
from io import StringIO
import pandas as pd
import os
from datetime import datetime

add_participant_bp = Blueprint('add_participant_bp', __name__)

# Define possible column name variations
first_name_variants = ['First Name', 'Name (First Name)', 'FirstName', 'First_Name', 'FirstName']
last_name_variants = ['Last Name', 'Name (Last Name)', 'LastName', 'Last_Name', 'LastName']
age_variants = ['Age', 'age']
city_variants = ['City', 'Address (City)', 'city']
state_variants = ['State', 'Address (State)', 'state']

# Function to find matching column name
def find_column(variants, headers):
    # First try exact match
    for variant in variants:
        if variant in headers:
            return variant
    
    # Then try case-insensitive match
    headers_lower = [h.lower() for h in headers]
    for variant in variants:
        if variant.lower() in headers_lower:
            idx = headers_lower.index(variant.lower())
            return headers[idx]
    
    # Finally try without spaces
    headers_nospace = [''.join(h.split()) for h in headers]
    variants_nospace = [''.join(v.split()) for v in variants]
    for variant in variants_nospace:
        if variant.lower() in [h.lower() for h in headers_nospace]:
            idx = [h.lower() for h in headers_nospace].index(variant.lower())
            return headers[idx]
    
    return None

def process_participant_data(df):
    success_count = 0
    error_count = 0
    
    # Get the actual column names from the DataFrame
    headers = df.columns.tolist()
    first_name_col = find_column(first_name_variants, headers)
    last_name_col = find_column(last_name_variants, headers)
    age_col = find_column(age_variants, headers)
    city_col = find_column(city_variants, headers)
    state_col = find_column(state_variants, headers)
    
    # Verify required columns exist
    if not all([first_name_col, last_name_col, age_col]):
        return False, "File must contain First Name, Last Name, and Age columns"
    
    for _, row in df.iterrows():
        try:
            # Extract and clean data
            first_name = str(row[first_name_col]).strip()
            last_name = str(row[last_name_col]).strip()
            age = int(float(str(row[age_col]).strip()))  # Handle both string and float inputs
            city = str(row[city_col]).strip() if city_col and not pd.isna(row[city_col]) else None
            state = str(row[state_col]).strip() if state_col and not pd.isna(row[state_col]) else None
            
            # Validate data
            if not first_name or not last_name or age < 0 or pd.isna(age):
                error_count += 1
                continue
            
            # Create new participant
            new_participant = Participant(
                first_name=first_name,
                last_name=last_name,
                age=age,
                city=city if city and city.lower() != 'nan' else None,
                state=state if state and state.lower() != 'nan' else None
            )
            
            db.session.add(new_participant)
            success_count += 1
            
        except (ValueError, KeyError) as e:
            error_count += 1
            continue
    
    if success_count > 0:
        db.session.commit()
    
    message = f"Added {success_count} participants successfully."
    if error_count > 0:
        message += f" {error_count} entries had errors and were skipped."
    
    return True, message

@add_participant_bp.route("/addParticipant", methods=['GET'])
def add_participant_page():
    return render_template("addParticipant.html")

@add_participant_bp.route("/addParticipant", methods=['POST'])
def add_participant():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    age = request.form.get("age")
    city = request.form.get("city")
    state = request.form.get("state")
    
    try:
        age = int(age)
    except ValueError:
        return render_template("addParticipant.html", error="Age must be a number")
    
    if not first_name or not last_name:
        return render_template("addParticipant.html", error="First name and last name are required")
    
    if age < 0:
        return render_template("addParticipant.html", error="Age cannot be negative")
    
    new_participant = Participant(
        first_name=first_name,
        last_name=last_name,
        age=age,
        city=city if city else None,
        state=state if state else None
    )
    
    db.session.add(new_participant)
    db.session.commit()
    
    return render_template("addParticipant.html", success="Participant added successfully")

@add_participant_bp.route('/addParticipantsFromFile', methods=['POST'])
def addParticipantsFromFile():
    if 'file' not in request.files:
        return render_template("addParticipant.html", error="No file uploaded")
    
    file = request.files['file']
    if file.filename == '':
        return render_template("addParticipant.html", error="No file selected")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.csv', '.xlsx', '.xls']:
        return render_template("addParticipant.html", error="File must be a CSV or Excel file (.csv, .xlsx, .xls)")
    
    try:
        if file_ext == '.csv':
            # Read CSV file
            df = pd.read_csv(file)
        else:
            # Read Excel file
            df = pd.read_excel(file)
        
        success, message = process_participant_data(df)
        if success:
            return render_template("addParticipant.html", success=message)
        else:
            return render_template("addParticipant.html", error=message)
        
    except Exception as e:
        return render_template("addParticipant.html", error=f"Error processing file: {str(e)}")

# Function Delete Participant
@add_participant_bp.route('/delete/<int:participant_id>')
def delete_participant(participant_id):
    participant = Participant.query.get(participant_id)
    if participant:
        db.session.delete(participant)
        db.session.commit()
    return redirect('/addParticipant')

# Function to render the edit participant page
@add_participant_bp.route('/edit/<int:participant_id>', methods=['GET'])
def edit_participant_page(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    return render_template("editParticipant.html", participant=participant)
