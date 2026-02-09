from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Тарифы (можно настроить)
TARIFFS = {
    "rent_per_m2": 50,           # руб/м² (квартплата)
    "cold_water": 35,            # руб/м³
    "hot_water": 150,            # руб/м³
    "electricity": 5.5,          # руб/кВт⋅ч
    "gas": 7.5,                  # руб/м³
    "garbage": 200,              # руб/месяц
    "maintenance": 1500          # руб/месяц
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    
    if request.method == "POST":
        apartment = request.form.get("apartment", "")
        area = float(request.form.get("area", 0))
        cold_water = float(request.form.get("cold_water", 0))
        hot_water = float(request.form.get("hot_water", 0))
        electricity = float(request.form.get("electricity", 0))
        gas = float(request.form.get("gas", 0))
        debt = float(request.form.get("debt", 0))
        
        # Расчёт
        rent = area * TARIFFS["rent_per_m2"]
        cold_cost = cold_water * TARIFFS["cold_water"]
        hot_cost = hot_water * TARIFFS["hot_water"]
        elec_cost = electricity * TARIFFS["electricity"]
        gas_cost = gas * TARIFFS["gas"]
        garbage_cost = TARIFFS["garbage"]
        maintenance_cost = TARIFFS["maintenance"]
        
        total = rent + cold_cost + hot_cost + elec_cost + gas_cost + garbage_cost + maintenance_cost
        total_with_debt = total + debt
        
        result = {
            "apartment": apartment,
            "area": area,
            "rent": round(rent, 2),
            "cold_water": cold_water,
            "cold_cost": round(cold_cost, 2),
            "hot_water": hot_water,
            "hot_cost": round(hot_cost, 2),
            "electricity": electricity,
            "elec_cost": round(elec_cost, 2),
            "gas": gas,
            "gas_cost": round(gas_cost, 2),
            "garbage_cost": garbage_cost,
            "maintenance_cost": maintenance_cost,
            "subtotal": round(total, 2),
            "debt": debt,
            "total": round(total_with_debt, 2),
            "date": datetime.now().strftime("%d.%m.%Y")
        }
    
    return render_template("index.html", result=result, tariffs=TARIFFS)

@app.route("/tariffs")
def tariffs():
    return render_template("tariffs.html", tariffs=TARIFFS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5013, debug=True)
