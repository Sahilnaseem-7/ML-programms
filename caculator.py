from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows frontend API calls

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        num1 = float(data['num1'])
        num2 = float(data['num2'])
        operation = data['operation']  # Now receives 'add', 'subtract', etc.
        
        if operation == 'add':
            result = num1 + num2
        elif operation == 'subtract':
            result = num1 - num2
        elif operation == 'multiply':
            result = num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                return jsonify({'error': 'Division by zero is not allowed!'}), 400
            result = num1 / num2
        else:
            return jsonify({'error': 'Invalid operation!'}), 400
        
        return jsonify({'result': result})
    except (ValueError, KeyError, TypeError) as e:
        print(f"API Error: {e}")  # Log for debugging
        return jsonify({'error': 'Invalid input! Please provide valid numbers.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
 