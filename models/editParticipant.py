from flask import Blueprint, render_template, request, redirect
from datetime import datetime
from models import db
from models.addParticipant import Participant

edit_participant_bp = Blueprint('edit_participant', __name__)

@edit_participant_bp.route("/editParticipant")
def edit_participant_page():
    # Get all participants for the selection dropdown
    participants = Participant.query.all()
    success = request.args.get('success')
    return render_template("editParticipant.html", participants=participants, success=success)

@edit_participant_bp.route('/editParticipant/<int:participant_id>')
def get_participant(participant_id):
    # Find the participant by the id
    participant = Participant.query.get_or_404(participant_id)
    # Get all participants for the selection dropdown
    participants = Participant.query.all()
    success = request.args.get('success')
    return render_template("editParticipant.html", participant=participant, participants=participants, success=success)

@edit_participant_bp.route('/edit/<int:participant_id>', methods=['POST'])
def edit_participant(participant_id):
    # Find the participant by the id
    participant = Participant.query.get_or_404(participant_id)
    # Get all participants for the selection dropdown (in case of validation error)
    participants = Participant.query.all()
    
    try:
        # Get the data from the form
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        age = int(request.form.get("age"))
        city = request.form.get("city")
        state = request.form.get("state")
        
        # Update the participant's information if all fields are provided
        if first_name and last_name and age:
            participant.first_name = first_name
            participant.last_name = last_name
            participant.age = age
            participant.city = city
            participant.state = state
            
            db.session.commit()
            return redirect(f"/editParticipant/{participant_id}?success=Participant+updated+successfully")
        else:
            return render_template("editParticipant.html", 
                                 participant=participant, 
                                 participants=participants, 
                                 error="All fields are required")
    except ValueError:
        return render_template("editParticipant.html", 
                             participant=participant, 
                             participants=participants, 
                             error="Invalid age format. Please enter a number")

@edit_participant_bp.route('/delete/<int:participant_id>', methods=['POST'])
def delete_participant(participant_id):
    try:
        # Find the participant by the id
        participant = Participant.query.get_or_404(participant_id)
        
        # Delete the participant
        print("attempting to delete",participant)
        db.session.delete(participant)
        db.session.commit()
        
        return redirect("/home")
    except Exception as e:
        print("failed to delete")
        participants = Participant.query.all()
        return render_template("editParticipant.html", 
                             participants=participants,
                             error="Could not delete participant. They may have associated scores.")
