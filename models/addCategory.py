from flask import Blueprint, render_template, redirect, request
from sqlalchemy import select
from models import db
from models.addParticipant import Participant
from models.tables import Category, Participant, Participant_Categories, add_participant_to_category, remove_participant_from_category
from random import shuffle

# MOVED TABLES TO THEIR OWN FILE

manage_category_bp = Blueprint('add_category_bp', __name__)

@manage_category_bp.route('/addCategory', methods=['GET','POST'])
@manage_category_bp.route('/addCategory/<string:selected_category_name>', methods=['GET','POST'])
def manage_category(selected_category_name = ""):

    current_category = Category.query.get(selected_category_name)

    if (request.method == 'POST'):
        print("Received POST from source:", request.form.get("source"))

        #adding a new category
        if (request.form.get("source") == "add_category"):
            new_category = Category(
                category_name = request.form.get("category_name"),
                criteria_count = int(request.form.get("criteria_count"))
            )

            existing = Category.query.filter(
                Category.category_name == new_category.category_name,
            ).first()

            if (existing):
                print("CATEGORY ALREADY EXISTS")
            else:
                db.session.add(new_category)
                db.session.commit()
            
            return redirect("/addCategory")
        
        #selecting a new category
        if (request.form.get("source") == "select"):
            return redirect("/addCategory" + "/" + request.form.get("category_name"))
        
        #adding a participant to a category
        if (request.form.get("source") == "add_participant"):
            add_participant_to_category(
                request.form.get("participant_id"),
                selected_category_name,
                -1
            )
            return redirect("/addCategory/" + selected_category_name)
        
        if (request.form.get("source") == "remove_participant"):
            remove_participant_from_category(
                request.form.get("participant_id"),
                selected_category_name
            )
            return redirect("/addCategory/" + selected_category_name)
        
        if (request.form.get("source") == "shuffle"):

            participants_to_shuffle = db.session.execute(
                select(
                    Participant.participant_id,
                )
                .join(Participant_Categories, Participant.participant_id == Participant_Categories.c.participant_id)
                .where(Participant_Categories.c.category_name == selected_category_name)
                .order_by(Participant_Categories.c.position)
            ).fetchall()

            print(participants_to_shuffle)

            for p in participants_to_shuffle:
                remove_participant_from_category(p.participant_id,selected_category_name)
            
            shuffle(participants_to_shuffle)
            for p in participants_to_shuffle:
                add_participant_to_category(p.participant_id,selected_category_name,-1)

            return redirect("/addCategory/" + selected_category_name)

        return redirect("/addCategory")


    else:
        categories = Category.query.all()
        participants = Participant.query.all()

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

        return render_template(
            "addCategory.html",
            categories=categories,
            participants=participants,
            category_participants=category_participants,
            selected_category_name=selected_category_name,
            max_position=len(category_participants) + 1
            )

