"""Replace date_of_birth with age

Revision ID: replace_dob_with_age
Revises: 3b40abf4e7ea
Create Date: 2025-04-09 11:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic
revision = 'replace_dob_with_age'
down_revision = '3b40abf4e7ea'
branch_labels = None
depends_on = None

def calculate_age(dob):
    today = datetime.now()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def upgrade():
    # Get the database connection
    connection = op.get_bind()
    
    # Check if age column exists
    inspector = Inspector.from_engine(connection)
    columns = [col['name'] for col in inspector.get_columns('participant')]
    
    # Create temporary table with new schema
    op.execute("""
        CREATE TABLE participant_new (
            participant_id INTEGER NOT NULL,
            first_name VARCHAR(15) NOT NULL,
            last_name VARCHAR(15) NOT NULL,
            age INTEGER NOT NULL,
            city VARCHAR(15),
            state VARCHAR(15),
            PRIMARY KEY (participant_id)
        )
    """)
    
    # Copy and transform data
    if 'date_of_birth' in columns:
        participants = connection.execute(sa.text(
            'SELECT participant_id, first_name, last_name, date_of_birth, city, state FROM participant'
        )).fetchall()
        
        for p in participants:
            dob = datetime.strptime(p[3], '%Y-%m-%d')
            age = calculate_age(dob)
            connection.execute(sa.text("""
                INSERT INTO participant_new (participant_id, first_name, last_name, age, city, state)
                VALUES (:id, :fname, :lname, :age, :city, :state)
            """), {
                'id': p[0],
                'fname': p[1],
                'lname': p[2],
                'age': age,
                'city': p[4],
                'state': p[5]
            })
    else:
        participants = connection.execute(sa.text(
            'SELECT participant_id, first_name, last_name, age, city, state FROM participant'
        )).fetchall()
        
        for p in participants:
            connection.execute(sa.text("""
                INSERT INTO participant_new (participant_id, first_name, last_name, age, city, state)
                VALUES (:id, :fname, :lname, :age, :city, :state)
            """), {
                'id': p[0],
                'fname': p[1],
                'lname': p[2],
                'age': p[3],
                'city': p[4],
                'state': p[5]
            })
    
    # Drop old table and rename new one
    op.drop_table('participant')
    op.rename_table('participant_new', 'participant')

def downgrade():
    # Create temporary table with old schema
    op.execute("""
        CREATE TABLE participant_new (
            participant_id INTEGER NOT NULL,
            first_name VARCHAR(15) NOT NULL,
            last_name VARCHAR(15) NOT NULL,
            date_of_birth DATE NOT NULL,
            city VARCHAR(15),
            state VARCHAR(15),
            PRIMARY KEY (participant_id)
        )
    """)
    
    # Copy data back, setting an approximate birth date
    connection = op.get_bind()
    participants = connection.execute(sa.text(
        'SELECT participant_id, first_name, last_name, age, city, state FROM participant'
    )).fetchall()
    
    for p in participants:
        connection.execute(sa.text("""
            INSERT INTO participant_new (participant_id, first_name, last_name, date_of_birth, city, state)
            VALUES (:id, :fname, :lname, date('now', '-' || :age || ' years'), :city, :state)
        """), {
            'id': p[0],
            'fname': p[1],
            'lname': p[2],
            'age': p[3],
            'city': p[4],
            'state': p[5]
        })
    
    # Drop old table and rename new one
    op.drop_table('participant')
    op.rename_table('participant_new', 'participant')
