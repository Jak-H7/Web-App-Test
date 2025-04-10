#This file initializes the database and will be 
#imported in the other models files

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Creating an instance of the database
db = SQLAlchemy()
migrate = Migrate()

def empty_database():
    """Empty all tables in the database."""
    # Import all models to ensure they are known to SQLAlchemy
    from .tables import Participant, Category, Score, Participant_Categories
    
    # Drop all tables
    db.session.query(Score).delete()
    db.session.query(Participant_Categories).delete()
    db.session.query(Participant).delete()
    db.session.query(Category).delete()
    
    # Commit the changes
    db.session.commit()