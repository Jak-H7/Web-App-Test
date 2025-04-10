from flask import Blueprint, render_template, redirect, request
from models import db
from models.tables import Score, Category, Participant, Participant_Categories, add_score, delete_score
from sqlalchemy import select, desc
from datetime import datetime

enter_scores_bp = Blueprint('enter_scores_bp', __name__)

@enter_scores_bp.route("/enterScores", methods=['GET','POST'])
@enter_scores_bp.route("/enterScores/<string:selected_category_name>/<int:judge_count>", methods=['GET','POST'])
def enter_scores(selected_category_name="",judge_count=3):
    
    if (request.method == 'POST'):
        print({a:request.form[a] for a in request.form})
        if (request.form.get("source") == "select"):
            return redirect("/enterScores" + "/" + request.form.get("category_name") + "/" + request.form.get("judge_count"))
        
        if (request.form.get("source") == "score_submit"):
            participant_id = int(request.form.get("participant_id"))
            score = float(request.form.get("score"))
            
            success, message = add_score(participant_id, selected_category_name, score)
            
            if not success:
                print("Error:", message)
                
            return redirect("/enterScores/" + selected_category_name + "/" + str(judge_count))
    
    tie = False
    criteria_count = 0
    scores = []
    category_participants = []
    
    if selected_category_name:
        category = Category.query.get(selected_category_name)
        if category:
            criteria_count = category.criteria_count
            
            scores = Score.query.filter(
                Score.category_name == selected_category_name
            ).order_by(Score.participant_id, Score.offset).all()
            
            category_participants = db.session.execute(
                select(Participant, Participant_Categories.c.position)
                .join(Participant_Categories, Participant.participant_id == Participant_Categories.c.participant_id)
                .where(Participant_Categories.c.category_name == selected_category_name)
                .order_by(Participant_Categories.c.position)
            ).fetchall()
            
            # Check for ties
            participants_scores = {}
            for score in scores:
                if score.offset <= judge_count:  # Only consider main scores, not tiebreakers
                    if score.participant_id not in participants_scores:
                        participants_scores[score.participant_id] = 0
                    participants_scores[score.participant_id] += score.score
            
            # Look for duplicate scores
            scores_list = list(participants_scores.values())
            if len(scores_list) != len(set(scores_list)):
                tie = True
                print("TIE DETECTED")
            
            # If there's a tie, only show the tied participants
            if tie:
                tied_scores = {}
                for pid, total in participants_scores.items():
                    if list(participants_scores.values()).count(total) > 1:
                        tied_scores[pid] = total
                category_participants = [p for p in category_participants if p.participant_id in tied_scores]

    return render_template(
        "enterScores.html",
        categories=Category.query.all(),
        selected_category_name=selected_category_name,
        judge_count=judge_count,
        category_participants=category_participants,
        criteria_count=criteria_count,
        scores=scores,
        tie=tie,
        now=datetime.now()  # Add current date for the print view
    )

@enter_scores_bp.route("/enterScores/<string:selected_category_name>/<int:judge_count>/<int:position>", methods=['GET','POST'])
def enter_scores2(selected_category_name="",judge_count=3,position=1):
    
    if (request.method == 'POST'):
        print({a:request.form[a] for a in request.form})        
        if (request.form.get("source") == "score_submit"):
            
            participant = request.form.get("participant_id")
            participant = participant.strip("()")
            participant = participant.split(",")
            
            participant_id = int(participant[0])
            participant_position = int(participant[1])
            selected_category = Category.query.get(selected_category_name)
            criteria_count = selected_category.criteria_count

            scores = []
            for judge in range(judge_count):
                judge_score = 0
                for criteria in range(criteria_count):
                    judge_score += float(request.form.get("judge_" + str(judge) + "_" + str(criteria)))
                scores.append(judge_score)
            score = sum(scores)/len(scores)

            add_score(participant_id,selected_category_name,score)

            return redirect("/enterScores" + "/" + selected_category_name + "/" + str(judge_count) + "/" + str(participant_position + 1))

        if (request.form.get("source") == "delete"):
            print(delete_score(
                int(request.form.get("participant_id")),
                selected_category_name
            ))
            return redirect("/enterScores" + "/" + selected_category_name + "/" + str(judge_count) + "/1")

        return redirect("/enterScores")
    else:

        selected_category = Category.query.get(selected_category_name)

        criteria_count = 0
        if selected_category:
            criteria_count = selected_category.criteria_count
        print("Criteria Count:",criteria_count)


        category_participants = db.session.execute(
            select(
                Participant.participant_id,
                Participant.first_name,
                Participant.last_name,
                Participant.city,
                Participant.state,
                Participant_Categories.c.position
            )
            .join(Participant_Categories, Participant.participant_id == Participant_Categories.c.participant_id)
            .where(Participant_Categories.c.category_name == selected_category_name)
            .order_by(Participant_Categories.c.position)
        ).fetchall()

        scores = []
        if selected_category:
            scores = db.session.execute(
                select(
                    Score.participant_id,
                    Score.category_name,
                    Score.score,
                    Participant.first_name,
                    Participant.last_name,
                )
                .join(Participant, Score.participant_id == Participant.participant_id)
                .where(Score.category_name == selected_category_name)
                .order_by(desc(Score.score))
            ).fetchall()
            print(scores)

        #check for duplicates
        i = 1
        tie = False
        while i < len(scores):
            if (scores[i].score == scores[i-1].score and scores[i].score != 0):
                tie = True
                break
            i += 1
        
        if tie:
            category_participants = [p for p in category_participants if (p.participant_id == scores[i].participant_id) or (p.participant_id == scores[i-1].participant_id) ]

        print("TIE:",tie)
        print(category_participants)

        return render_template(
            "enterScores2.html",
            categories=Category.query.all(),
            selected_category_name=selected_category_name,
            judge_count=judge_count,
            category_participants=category_participants,
            criteria_count=criteria_count,
            scores=scores,
            tie=tie,
            position=position
        )