from main import app
from models.user import db, User

def create_user(username, password):
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"User '{username}' already exists.")
            return

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' created successfully.")

# Create the predefined users
if __name__ == "__main__":
    users = [
        ("Fiddler159#", "TuneUp2025!"),

    ]

    for username, password in users:
        create_user(username, password)