from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apartments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    area = db.Column(db.Float, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    total_floors = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')
    description = db.Column(db.Text)
    owner_name = db.Column(db.String(100))
    owner_phone = db.Column(db.String(20))

    def __repr__(self):
        return f'<Apartment {self.address}>'

class ApartmentForm(FlaskForm):
    address = StringField('Адрес', validators=[DataRequired()])
    rooms = IntegerField('Количество комнат', validators=[DataRequired(), NumberRange(min=1, max=10)])
    area = FloatField('Площадь (м²)', validators=[DataRequired(), NumberRange(min=1)])
    floor = IntegerField('Этаж', validators=[DataRequired(), NumberRange(min=1)])
    total_floors = IntegerField('Всего этажей', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Цена (руб.)', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Статус', choices=[('available', 'Доступна'), ('sold', 'Продана'), ('reserved', 'Забронирована')])
    description = TextAreaField('Описание')
    owner_name = StringField('Имя владельца')
    owner_phone = StringField('Телефон владельца')

@app.route('/')
def index():
    apartments = Apartment.query.all()
    return render_template('index.html', apartments=apartments)

@app.route('/add', methods=['GET', 'POST'])
def add_apartment():
    form = ApartmentForm()
    if form.validate_on_submit():
        apartment = Apartment(
            address=form.address.data,
            rooms=form.rooms.data,
            area=form.area.data,
            floor=form.floor.data,
            total_floors=form.total_floors.data,
            price=form.price.data,
            status=form.status.data,
            description=form.description.data,
            owner_name=form.owner_name.data,
            owner_phone=form.owner_phone.data
        )
        db.session.add(apartment)
        db.session.commit()
        flash('Квартира успешно добавлена!', 'success')
        return redirect(url_for('index'))
    return render_template('add.html', form=form)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_apartment(id):
    apartment = Apartment.query.get_or_404(id)
    form = ApartmentForm(obj=apartment)
    if form.validate_on_submit():
        form.populate_obj(apartment)
        db.session.commit()
        flash('Квартира успешно обновлена!', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, apartment=apartment)

@app.route('/delete/<int:id>')
def delete_apartment(id):
    apartment = Apartment.query.get_or_404(id)
    db.session.delete(apartment)
    db.session.commit()
    flash('Квартира успешно удалена!', 'success')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    rooms = request.args.get('rooms', type=int)
    
    apartments = Apartment.query
    
    if query:
        apartments = apartments.filter(Apartment.address.contains(query))
    if min_price:
        apartments = apartments.filter(Apartment.price >= min_price)
    if max_price:
        apartments = apartments.filter(Apartment.price <= max_price)
    if rooms:
        apartments = apartments.filter(Apartment.rooms == rooms)
    
    apartments = apartments.all()
    return render_template('search.html', apartments=apartments)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5010, debug=True)