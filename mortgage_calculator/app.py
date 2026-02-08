from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

class MortgageCalculator:
    def __init__(self, loan_amount, interest_rate, loan_term_years, start_date=None):
        self.loan_amount = loan_amount
        self.annual_interest_rate = interest_rate / 100
        self.loan_term_years = loan_term_years
        self.loan_term_months = loan_term_years * 12
        self.monthly_interest_rate = self.annual_interest_rate / 12
        self.start_date = start_date or datetime.now()
        
    def calculate_monthly_payment(self):
        """Рассчитать ежемесячный платеж по аннуитетной схеме"""
        if self.monthly_interest_rate == 0:
            return self.loan_amount / self.loan_term_months
        
        monthly_payment = (self.loan_amount * 
                          (self.monthly_interest_rate * (1 + self.monthly_interest_rate) ** self.loan_term_months) /
                          ((1 + self.monthly_interest_rate) ** self.loan_term_months - 1))
        return round(monthly_payment, 2)
    
    def generate_payment_schedule(self):
        """Генерировать график платежей"""
        monthly_payment = self.calculate_monthly_payment()
        remaining_balance = self.loan_amount
        schedule = []
        
        for month in range(1, self.loan_term_months + 1):
            interest_payment = remaining_balance * self.monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment
            
            payment_date = self.start_date + relativedelta(months=month)
            
            schedule.append({
                'month': month,
                'date': payment_date.strftime('%Y-%m-%d'),
                'payment': round(monthly_payment, 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'balance': round(max(0, remaining_balance), 2)
            })
        
        return schedule
    
    def calculate_summary(self):
        """Рассчитать общую информацию по кредиту"""
        monthly_payment = self.calculate_monthly_payment()
        total_payments = monthly_payment * self.loan_term_months
        total_interest = total_payments - self.loan_amount
        
        return {
            'loan_amount': self.loan_amount,
            'monthly_payment': monthly_payment,
            'total_payments': round(total_payments, 2),
            'total_interest': round(total_interest, 2),
            'interest_percentage': round((total_interest / self.loan_amount) * 100, 2)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        loan_amount = float(data['loan_amount'])
        interest_rate = float(data['interest_rate'])
        loan_term = int(data['loan_term'])
        
        calculator = MortgageCalculator(loan_amount, interest_rate, loan_term)
        
        summary = calculator.calculate_summary()
        schedule = calculator.generate_payment_schedule()
        
        # Создаем график
        months = [item['month'] for item in schedule]
        principal_payments = [item['principal'] for item in schedule]
        interest_payments = [item['interest'] for item in schedule]
        balances = [item['balance'] for item in schedule]
        
        # График структуры платежей
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=months, y=principal_payments,
            mode='lines+markers',
            name='Основной долг',
            line=dict(color='blue')
        ))
        fig1.add_trace(go.Scatter(
            x=months, y=interest_payments,
            mode='lines+markers',
            name='Проценты',
            line=dict(color='red')
        ))
        fig1.update_layout(
            title='Структура ежемесячных платежей',
            xaxis_title='Месяц',
            yaxis_title='Сумма (руб)',
            hovermode='x unified'
        )
        
        # График остатка задолженности
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=months, y=balances,
            mode='lines',
            name='Остаток долга',
            fill='tonexty',
            line=dict(color='green')
        ))
        fig2.update_layout(
            title='Остаток задолженности по месяцам',
            xaxis_title='Месяц',
            yaxis_title='Остаток (руб)'
        )
        
        graphs = {
            'payments_structure': json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder),
            'balance_chart': json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'schedule': schedule[:12],  # Показываем первые 12 месяцев
            'full_schedule': schedule,
            'graphs': graphs
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_schedule/<loan_amount>/<interest_rate>/<loan_term>')
def download_schedule(loan_amount, interest_rate, loan_term):
    try:
        calculator = MortgageCalculator(
            float(loan_amount), 
            float(interest_rate), 
            int(loan_term)
        )
        
        schedule = calculator.generate_payment_schedule()
        df = pd.DataFrame(schedule)
        
        # Конвертируем в CSV
        csv_data = df.to_csv(index=False, encoding='utf-8')
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=mortgage_schedule.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3001)