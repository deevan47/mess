from flask import Flask, request, jsonify, render_template # Added render_template
from datetime import datetime
from flask_cors import CORS # Import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# In-memory data store for demonstration purposes
# In a real application, this would be a database
mess_data = {
    "2023-10-27": {
        "breakfast": [
            {"item": "Idli", "quantity": 4},
            {"item": "Sambar", "quantity": "unlimited"}
        ],
        "lunch": [
            {"item": "Rice", "quantity": "unlimited"},
            {"item": "Dal Fry", "quantity": 1},
            {"item": "Mix Veg Curry", "quantity": 1}
        ],
        "dinner": [
            {"item": "Roti", "quantity": 3},
            {"item": "Chicken Curry", "quantity": 1}
        ]
    }
    # You can add more dates here
}

# Helper function to get today's date in YYYY-MM-DD format
def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")

# --- Frontend Routes (to serve HTML files) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add')
def add_item_page():
    return render_template('add_item.html')

@app.route('/edit')
def edit_item_page():
    return render_template('edit_item.html')

@app.route('/delete')
def delete_item_page():
    return render_template('delete_item.html')

# --- API Endpoints (as before) ---

# 1. Base Endpoint: Get all mess food data for a specific date (or today if not specified)
@app.route('/api/mess', methods=['GET']) # Changed to /api/mess to differentiate from frontend route
def get_all_mess_food():
    date_str = request.args.get('date', get_today_date_str())
    if date_str in mess_data:
        return jsonify(mess_data[date_str])
    return jsonify({"message": f"No mess food data found for {date_str}"}), 404

# 2. Endpoint to add/update/delete items for a specific meal type
@app.route('/api/mess/<meal_type>', methods=['GET', 'POST', 'PUT', 'DELETE']) # Changed to /api/mess/<meal_type>
def manage_meal_food(meal_type):
    date_str = request.args.get('date', get_today_date_str())

    if meal_type not in ['breakfast', 'lunch', 'dinner']:
        return jsonify({"message": "Invalid meal type. Must be 'breakfast', 'lunch', or 'dinner'."}), 400

    if date_str not in mess_data:
        # Initialize an empty structure for the new date
        mess_data[date_str] = {"breakfast": [], "lunch": [], "dinner": []}

    current_meal = mess_data[date_str][meal_type]

    if request.method == 'GET':
        return jsonify(current_meal)

    elif request.method == 'POST':
        # Add a new food item to the meal
        new_item = request.json
        if not new_item or 'item' not in new_item:
            return jsonify({"message": "Missing 'item' field in request body."}), 400
        current_meal.append(new_item)
        return jsonify({"message": f"Item added to {meal_type}", "data": new_item}), 201

    elif request.method == 'PUT':
        # Update an existing food item in the meal
        updated_item = request.json
        if not updated_item or 'item' not in updated_item:
            return jsonify({"message": "Missing 'item' field in request body for update."}), 400

        item_found = False
        for i, food_item in enumerate(current_meal):
            if food_item['item'].lower() == updated_item['item'].lower():
                current_meal[i].update(updated_item) # Update existing fields
                item_found = True
                break
        if item_found:
            return jsonify({"message": f"Item '{updated_item['item']}' updated in {meal_type}", "data": updated_item})
        return jsonify({"message": f"Item '{updated_item['item']}' not found in {meal_type} for update."}), 404

    elif request.method == 'DELETE':
        # Delete a food item from the meal
        item_to_delete = request.json
        if not item_to_delete or 'item' not in item_to_delete:
            return jsonify({"message": "Missing 'item' field in request body for deletion."}), 400

        original_len = len(current_meal)
        mess_data[date_str][meal_type] = [
            food_item for food_item in current_meal
            if food_item['item'].lower() != item_to_delete['item'].lower()
        ]

        if len(mess_data[date_str][meal_type]) < original_len:
            return jsonify({"message": f"Item '{item_to_delete['item']}' deleted from {meal_type}"})
        return jsonify({"message": f"Item '{item_to_delete['item']}' not found in {meal_type} for deletion."}), 404


if __name__ == '__main__':
    app.run(debug=True)