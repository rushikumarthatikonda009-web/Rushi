from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initial values
INITIAL_BALANCE = 30000.0
INITIAL_GOLD = 30.0  # grams

# In-memory expense storage
expenses = []

# Helper functions
def auto_categorize(name):
    name = name.lower()
    if any(k in name for k in ["pizza", "restaurant", "snack"]):
        return "Food"
    if any(k in name for k in ["bus", "metro", "uber", "taxi"]):
        return "Transport"
    if any(k in name for k in ["movie", "game", "netflix"]):
        return "Entertainment"
    if any(k in name for k in ["gold", "jewellery", "jewel"]):
        return "Gold"
    return "Other"


def calculate_summary():
    total_spent = sum(exp['amount'] for exp in expenses)
    current_balance = INITIAL_BALANCE - total_spent
    gold_holdings = INITIAL_GOLD + sum(
        exp['amount'] / 7000 for exp in expenses if exp['category'] == 'Gold'
    )  # ₹7000 per gram approx.
    
    avg_daily_spent = total_spent / len(expenses) if expenses else 0
    predicted_next_month = avg_daily_spent * 30 * 1.1  # 10% growth factor
    
    budget_alert = "On Track ✔️" if total_spent <= INITIAL_BALANCE * 0.9 else "Budget Exceeded ⚠️"
    
    return {
        "total_spent": round(total_spent, 2),
        "current_balance": round(current_balance, 2),
        "gold_holdings": round(gold_holdings, 2),
        "predicted_next_month": round(predicted_next_month, 2),
        "budget_alert": budget_alert,
    }


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    summary = calculate_summary()
    return jsonify({
        "expenses": expenses,
        **summary
    })


@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    name = data.get('name')
    amount = data.get('amount')
    category = data.get('category')
    date_str = data.get('date')
    
    # Validate input
    if not all([name, amount, category, date_str]):
        return jsonify({"error": "Missing fields"}), 400
    
    # Parse date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400
    
    # Auto categorize if category is Other
    if category == "Other":
        category = auto_categorize(name)
    
    expense = {
        "id": len(expenses) + 1,
        "name": name,
        "amount": float(amount),
        "category": category,
        "date": date_obj.isoformat()
    }
    expenses.append(expense)
    
    return jsonify(expense), 201


@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    global expenses
    expenses = [exp for exp in expenses if exp['id'] != expense_id]
    return '', 204


if __name__ == '__main__':
    app.run(debug=True, port=5000)
