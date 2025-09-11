from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/calculate', methods=['GET'])
def calculate():
    # get values from query params
    num1 = float(request.args.get("num1", 0))
    num2 = float(request.args.get("num2", 0))
    operation = request.args.get("operation", "add")

    if operation == "add":
        result = num1 + num2
    elif operation == "subtract":
        result = num1 - num2
    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        result = num1 / num2 if num2 != 0 else "Cannot divide by zero"
    else:
        result = "Invalid operation"

    return jsonify({
        "num1": num1,
        "num2": num2,
        "operation": operation,
        "result": result
    })

if __name__ == '__main__':
    app.run(debug=True)

