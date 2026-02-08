from flask import Flask, render_template, request, jsonify
import math
import re

app = Flask(__name__)

class Calculator:
    def __init__(self):
        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'log': math.log10,
            'ln': math.log,
            'sqrt': math.sqrt,
            'abs': abs,
            'exp': math.exp,
            'factorial': math.factorial
        }
        
        self.constants = {
            'pi': math.pi,
            'e': math.e
        }
    
    def prepare_expression(self, expression):
        # Заменяем константы
        for const, value in self.constants.items():
            expression = expression.replace(const, str(value))
        
        # Заменяем функции
        for func_name, func in self.functions.items():
            pattern = f'{func_name}\\(([^)]+)\\)'
            matches = re.findall(pattern, expression)
            for match in matches:
                try:
                    arg_value = self.evaluate_safe(match)
                    if func_name == 'factorial':
                        result = func(int(arg_value))
                    else:
                        result = func(arg_value)
                    expression = expression.replace(f'{func_name}({match})', str(result), 1)
                except Exception as e:
                    raise ValueError(f'Ошибка в функции {func_name}: {str(e)}')
        
        return expression
    
    def evaluate_safe(self, expression):
        # Безопасная оценка математических выражений
        allowed_chars = '0123456789+-*/.() '
        allowed_names = {'__builtins__': {}}
        
        if not all(c in allowed_chars for c in expression.replace('e', '').replace('E', '')):
            # Проверяем на научную нотацию
            if not re.match(r'^[0-9+\-*/.()\s eE]+$', expression):
                raise ValueError('Недопустимые символы в выражении')
        
        try:
            return eval(expression, allowed_names)
        except ZeroDivisionError:
            raise ValueError('Деление на ноль')
        except Exception as e:
            raise ValueError(f'Ошибка вычисления: {str(e)}')
    
    def calculate(self, expression):
        try:
            # Убираем пробелы
            expression = expression.replace(' ', '')
            
            # Заменяем × и ÷ на стандартные операторы
            expression = expression.replace('×', '*').replace('÷', '/')
            
            # Обрабатываем функции и константы
            processed_expression = self.prepare_expression(expression)
            
            # Вычисляем результат
            result = self.evaluate_safe(processed_expression)
            
            # Форматируем результат
            if isinstance(result, float):
                if result.is_integer():
                    return str(int(result))
                else:
                    return f'{result:.10g}'
            
            return str(result)
            
        except Exception as e:
            return f'Ошибка: {str(e)}'

calc = Calculator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '')
    
    result = calc.calculate(expression)
    
    return jsonify({
        'result': result,
        'expression': expression
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3001)