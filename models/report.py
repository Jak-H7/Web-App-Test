from flask import Blueprint, render_template, request
from models import db
from models.tables import Category, Participant, Participant_Categories, Score
from sqlalchemy import select

report_bp = Blueprint('report_bp', __name__)

@report_bp.route("/report", methods=['GET'])
def report():
    selected_category = None
    competition_results = {}

    category_name = request.args.get('category_name')
    if category_name:
        selected_category = Category.query.get(category_name)
        if selected_category:
            # Get all participants and their scores for this category
            participants = db.session.execute(
                select(Participant, Participant_Categories.c.position)
                .join(Participant_Categories, Participant.participant_id == Participant_Categories.c.participant_id)
                .where(Participant_Categories.c.category_name == category_name)
                .order_by(Participant_Categories.c.position)
            ).fetchall()

            category_results = []
            for participant_row in participants:
                participant = participant_row[0]  # Get the Participant object
                position = participant_row[1]     # Get the position value
                
                scores = Score.query.filter_by(
                    participant_id=participant.participant_id,
                    category_name=category_name
                ).all()
                total_score = sum(score.score for score in scores)
                category_results.append({
                    'first_name': participant.first_name,
                    'last_name': participant.last_name,
                    'position': position,
                    'total_score': total_score
                })
            competition_results[category_name] = sorted(category_results, key=lambda x: (-x['total_score'], x['position']))

    return render_template(
        "report.html",
        categories=Category.query.order_by(Category.category_name).all(),
        selected_category=selected_category,
        competition_results=competition_results
    )