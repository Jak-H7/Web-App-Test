from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required
from models import db, migrate, empty_database
from models.addParticipant import add_participant_bp 
from models.home import home_bp
from models.addCategory import manage_category_bp
from models.enterScores import enter_scores_bp
from models.report import report_bp
from models.login import login_manager, login_bp
from models.editParticipant import edit_participant_bp

# Create the Flask app
app = Flask(__name__)
app.debug = True

# Adding configuration for using the sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fiddlers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(add_participant_bp)
app.register_blueprint(home_bp)
app.register_blueprint(enter_scores_bp)
app.register_blueprint(manage_category_bp)
app.register_blueprint(report_bp)
app.register_blueprint(login_bp)
app.register_blueprint(edit_participant_bp)

@app.route("/")
@login_required
def default():
    return redirect(url_for("home_bp.home"))

@app.cli.command("empty-db")
def empty_db_command():
    """Empty all tables in the database."""
    empty_database()
    print("Database emptied successfully!")

@app.shell_context_processor
def make_shell_context():
    from models.user import User
    return {"db": db, "User": User}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()(host="0.0.0.0", port=10000)