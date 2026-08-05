from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app) 

# Replace with your actual connection string
DATABASE_URL = "postgresql://neondb_owner:npg_po1uKOyPCSb0@ep-dry-heart-aut93f81-pooler.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # SQL query mapping database columns to match HTML JavaScript properties
        cursor.execute("""
            SELECT 
                id, 
                name, 
                category, 
                CAST(price AS FLOAT) AS price, 
                CAST(rating AS FLOAT) AS rating, 
                popularity, 
                date_added_days_ago AS "dateAdded", 
                in_stock AS "stock", 
                img_url AS "img", 
                badge, 
                range_miles AS "range", 
                top_speed_mph AS "topSpeed", 
                charging_time, 
                weight, 
                description AS "desc" 
            FROM products;
        """)
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jsonify(products)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ==========================================
# NEW: ENDPOINT TO SAVE NEWSLETTER SUBSCRIBERS
# ==========================================
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
            
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # ON CONFLICT prevents crashes if the same email is entered twice
        subscribe_query = """
            INSERT INTO subscribers (email) 
            VALUES (%s) 
            ON CONFLICT (email) DO NOTHING;
        """
        cursor.execute(subscribe_query, (email,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Subscribed successfully!"}), 201

    except Exception as e:
        print("Error saving subscriber:", e)
        return jsonify({"error": str(e)}), 500
# ==========================================
# NEW: ENDPOINT TO SAVE ORDERS & CART ITEMS
# ==========================================
@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 1. Insert the customer's details into the 'orders' table
        order_query = """
            INSERT INTO orders (full_name, email, street_address, city, zip_code, payment_method, subtotal, discount, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor.execute(order_query, (
            data['fullName'],
            data['email'],
            data['streetAddress'],
            data['city'],
            data['zipCode'],
            data['paymentMethod'],
            data['subtotal'],
            data['discount'],
            data['total']
        ))
        
        # Grab the newly generated Order ID from the database
        order_id = cursor.fetchone()[0]
        
        # 2. Insert each bike from their cart into the 'order_items' table
        item_query = """
            INSERT INTO order_items (order_id, product_id, quantity, price_at_time)
            VALUES (%s, %s, %s, %s);
        """
        for item in data['items']:
            cursor.execute(item_query, (
                order_id,
                item['id'],
                item['qty'],
                item['price']
            ))
            
        # Save changes and close connections
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Order saved successfully!", "order_id": order_id}), 201

    except Exception as e:
        print("Error saving order:", e)
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=5000)
