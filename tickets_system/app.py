from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Новая")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/")
def index():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template("index.html", tickets=tickets)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        ticket = Ticket(
            apartment=request.form["apartment"],
            description=request.form["description"]
        )
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/status/<int:id>/<status>")
def update_status(id, status):
    ticket = Ticket.query.get_or_404(id)
    ticket.status = status
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5011, debug=True)
