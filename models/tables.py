from models import db
from sqlalchemy import update, select, delete


Participant_Categories = db.Table('Participant_Categories',
    db.Column('position', db.Integer, nullable=False), #position should start at 1
    db.Column('participant_id', db.Integer, db.ForeignKey('participant.participant_id'), primary_key=True),
    db.Column('category_name', db.String(15), db.ForeignKey('category.category_name'), primary_key=True),
    db.UniqueConstraint('category_name', 'position', name='uq_category_position')  # Ensures unique position per category
)

class Participant(db.Model):
    # Participant id: Unique identifier for each participant
    # First Name: Name of the participant
    # Last Name: Last name of the participant
    # age: Age of the participant
    # city: City of the participant
    # state: State of the participant
    participant_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(15), nullable=False)
    last_name = db.Column(db.String(15), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(15), nullable=True)  # Temporarily nullable
    state = db.Column(db.String(15), nullable=True)  # Temporarily nullable
    categories = db.relationship('Category', secondary=Participant_Categories, back_populates='participants')

    def __repr__(self):
        return f"Participant('{self.participant_id}', '{self.first_name}', '{self.last_name}', '{self.age}', '{self.city}', '{self.state}')"
    
class Category(db.Model):
    category_name = db.Column(db.String(15), nullable=False, primary_key=True)
    criteria_count = db.Column(db.Integer, nullable=False)
    participants = db.relationship('Participant', secondary=Participant_Categories, back_populates='categories')

    def __repr__(self):
        return f"Category('category_name: {self.category_name}, criteria_count:{self.criteria_count}')"
    
def add_participant_to_category(participant_id, category_name, position=-0, push_back=True, correct_bounds=True):
    remove_participant_from_category(participant_id,category_name)
    try:
        participant = Participant.query.get(participant_id)
        category = Category.query.get(category_name)

        if not (participant and category):
            return False, "participant or category not found"
        
        if (position == -1):
            position = len(category.participants) + 1

        if correct_bounds:
                print("position before:",position)
                position = max(1,min(position,len(category.participants) + 1))
                print("corrected position to:",position)

        if (position > len(category.participants) + 1 or position < 1):
            return False, "out of bounds"

        if (position <= len(category.participants)):
            if (push_back):
                #have to do weird thing where I reverse the order
                #and update from the highest to lowest position because of uniqueness
                participants = db.session.execute(
                    select(Participant_Categories.c.participant_id, Participant_Categories.c.position)
                    .where(
                        (Participant_Categories.c.category_name == category_name) &
                        (Participant_Categories.c.position >= position)
                    )
                    .order_by(Participant_Categories.c.position.desc())
                ).fetchall()

                for p_id, p_pos in participants:
                    db.session.execute(
                        update(Participant_Categories)
                        .where(
                            (Participant_Categories.c.participant_id == p_id) &
                            (Participant_Categories.c.category_name == category_name)
                        )
                        .values(position=p_pos + 1)
                    )

                db.session.commit()

        insert_stmt = Participant_Categories.insert().values(
            participant_id=participant_id,
            category_name=category_name,
            position=position
        )

        db.session.execute(insert_stmt)
        db.session.commit()
        return True, "no issue"

    except Exception as e:
        return False, "exception"
    
def remove_participant_from_category(participant_id, category_name):
    try:
        participant_entry = db.session.execute(
            select(Participant_Categories)
            .where(
                (Participant_Categories.c.participant_id == participant_id) &
                (Participant_Categories.c.category_name == category_name)
            )
        ).fetchone()

        if not participant_entry:
            return False, "Participant not Found"
        
        position = participant_entry[0]

        db.session.execute(
            delete(Participant_Categories)
            .where(
                (Participant_Categories.c.participant_id == participant_id) &
                (Participant_Categories.c.category_name == category_name)
            )
        )

        db.session.execute(
            update(Participant_Categories)
            .where(
                (Participant_Categories.c.category_name == category_name) &
                (Participant_Categories.c.position > position)
            )
            .values(position=Participant_Categories.c.position - 1)
        )

        db.session.commit()
        return True, "no issue"
    except:
        return False, "exception"

class Score(db.Model):
    # score_id: Unique identifier for each score record
    # category_id: the id of the category the score belongs to
    # participant_id: the id of the participant
    score_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(15), nullable=False)
    participant_id = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Float, nullable=False)
    offset = db.Column(db.Integer, nullable=False, default=1)

def add_score(participant_id, category_name, score):
    try:
        new_score = Score(
            category_name=category_name,
            participant_id=participant_id,
            score=score
        )
        
        existing = Score.query.filter(
            Score.participant_id == participant_id,
            Score.category_name == category_name
        ).first()

        if existing:
            db.session.delete(existing)
        
        db.session.add(new_score)
        db.session.commit()
        
        return True, "no issue"

    except Exception as e:
        print(e)
        return False, "exception"

def delete_score(participant_id, category_name):
    existing = Score.query.filter(
        Score.participant_id == participant_id,
        Score.category_name == category_name
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return True, "score existed"
    
    return False, "score not found"
