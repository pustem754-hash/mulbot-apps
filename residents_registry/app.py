from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "residents-secret-key-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///residents.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    passport_series = db.Column(db.String(10), nullable=False)
    passport_number = db.Column(db.String(20), nullable=False)
    passport_issued_by = db.Column(db.Text)
    passport_issued_date = db.Column(db.String(50))
    birth_date = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
@app.route("/")
def index():
    search = request.args.get("search", "")
    if search:
        residents = Resident.query.filter(
            (Resident.apartment.contains(search)) |
            (Resident.full_name.contains(search)) |
            (Resident.passport_number.contains(search))
        ).all()
    else:
        residents = Resident.query.order_by(Resident.apartment).all()
    return render_template("index.html", residents=residents, search=search)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        resident = Resident(
            apartment=request.form["apartment"],
            full_name=request.form["full_name"],
            passport_series=request.form["passport_series"],
            passport_number=request.form["passport_number"],
            passport_issued_by=request.form.get("passport_issued_by", ""),
            passport_issued_date=request.form.get("passport_issued_date", ""),
            birth_date=request.form.get("birth_date", ""),
            phone=request.form.get("phone", ""),
            email=request.form.get("email", "")
        )
        db.session.add(resident)
        db.session.commit()
        flash("✅ Жилец успешно добавлен!", "success")
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    resident = Resident.query.get_or_404(id)
    if request.method == "POST":
        resident.apartment = request.form["apartment"]
        resident.full_name = request.form["full_name"]
        resident.passport_series = request.form["passport_series"]
        resident.passport_number = request.form["passport_number"]
        resident.passport_issued_by = request.form.get("passport_issued_by", "")
        resident.passport_issued_date = request.form.get("passport_issued_date", "")
        resident.birth_date = request.form.get("birth_date", "")
        resident.phone = request.form.get("phone", "")
        resident.email = request.form.get("email", "")
        db.session.commit()
        flash("✅ Данные обновлены!", "success")
        return redirect(url_for("index"))
    return render_template("edit.html", resident=resident)

@app.route("/delete/<int:id>")
def delete(id):
    resident = Resident.query.get_or_404(id)
    db.session.delete(resident)
    db.session.commit()
    flash("✅ Жилец удалён!", "success")
    return redirect(url_for("index"))

@app.route("/view/<int:id>")
def view(id):
    resident = Resident.query.get_or_404(id)
    return render_template("view.html", resident=resident)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5014, debug=True)
