from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///meters.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Meter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment = db.Column(db.String(50), nullable=False)
    cold_water = db.Column(db.Float, default=0)
    hot_water = db.Column(db.Float, default=0)
    electricity = db.Column(db.Float, default=0)
    gas = db.Column(db.Float, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_diff(self):
        prev = Meter.query.filter(
            Meter.apartment == self.apartment,
            Meter.date < self.date
        ).order_by(Meter.date.desc()).first()
        
        if prev:
            return {
                "cold": round(self.cold_water - prev.cold_water, 2),
                "hot": round(self.hot_water - prev.hot_water, 2),
                "electricity": round(self.electricity - prev.electricity, 2),
                "gas": round(self.gas - prev.gas, 2)
            }
        return None

@app.route("/")
def index():
    apartments = db.session.query(Meter.apartment).distinct().all()
    apartments = [a[0] for a in apartments]
    return render_template("index.html", apartments=apartments)

@app.route("/apartment/<apt>")
def apartment_history(apt):
    meters = Meter.query.filter_by(apartment=apt).order_by(Meter.date.desc()).all()
    return render_template("history.html", apartment=apt, meters=meters)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        meter = Meter(
            apartment=request.form["apartment"],
            cold_water=float(request.form["cold_water"]),
            hot_water=float(request.form["hot_water"]),
            electricity=float(request.form["electricity"]),
            gas=float(request.form.get("gas", 0))
        )
        db.session.add(meter)
        db.session.commit()
        return redirect(url_for("apartment_history", apt=meter.apartment))
    return render_template("add.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5012, debug=True)
