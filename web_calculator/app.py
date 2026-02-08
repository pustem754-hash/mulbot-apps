from flask import Flask, render_template, request, jsonify
import re
import operator

app = Flask(__name__)

# Безопасный калькулятор без eval()
def safe_calculate(expression):
    # Убираем пробелы
    expression = expression.replace(' ', '')
    
    # Замена символов
    expression = expression.replace('÷', '/').replace('×', '*')
    
    # Проверка на допустимые символы
    if not re.match(r'^[\d+\-*/().]+$', expression):
        raise ValueError("Недопустимые символы")
    
    # Проверка скобок
    if expression.count('(') != expression.count(')'):
        raise ValueError("Неправильные скобки")
    
    try:
        # Безопасное вычисление через ast
        import ast
        
        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                left = eval_expr(node.left)
                right = eval_expr(node.right)
                
                if isinstance(node.op, ast.Add):
                    return left + right
                elif isinstance(node.op, ast.Sub):
                    return left - right
                elif isinstance(node.op, ast.Mult):
                    return left * right
                elif isinstance(node.op, ast.Div):
                    if right == 0:
                        raise ZeroDivisionError("Деление на ноль")
                    return left / right
                elif isinstance(node.op, ast.Pow):
                    return left ** right
            elif isinstance(node, ast.UnaryOp):
                operand = eval_expr(node.operand)
                if isinstance(node.op, ast.USub):
                    return -operand
                elif isinstance(node.op, ast.UAdd):
                    return operand
            else:
                raise ValueError("Неподдерживаемая операция")
        
        tree = ast.parse(expression, mode='eval')
        result = eval_expr(tree.body)
        
        # Округление до 10 знаков
        if isinstance(result, float):
            result = round(result, 10)
        
        return result
    
    except ZeroDivisionError:
        raise
    except Exception as e:
        raise ValueError(f"Ошибка вычисления: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({'error': 'Пустое выражение'}), 400
        
        result = safe_calculate(expression)
        
        return jsonify({'result': result})
    
    except ZeroDivisionError:
        return jsonify({'error': 'Деление на ноль невозможно'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Ошибка вычисления'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
