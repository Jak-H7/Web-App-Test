from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.user import db, User

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login_bp.login_page"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create login Blueprint
login_bp = Blueprint('login_bp', __name__)

@login_bp.route("/userLogin", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home_bp.home"))  # Update with your dashboard route
        else:
            flash("Invalid username or password.", "danger")
    
    return render_template("userLogin.html")

@login_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login_bp.login_page"))