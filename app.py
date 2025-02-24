from flask import Flask, jsonify, request
import pyodbc
import os

app = Flask(__name__)

# Load configuration from environment variables
db_config = {
    'server': os.getenv('DB_SERVER', 'satwaserver.database.windows.net'),
    'database': os.getenv('DB_NAME', 'satwa'),
    'username': os.getenv('DB_USER', 'shinigami'),
    'password': os.getenv('DB_PASSWORD', 'Admin123'),  # Set this in Azure environment
    'driver': os.getenv('DB_DRIVER', '{ODBC Driver 18 for SQL Server}'),
}

connection_string = (
    f"DRIVER={db_config['driver']};"
    f"SERVER={db_config['server']};"
    f"DATABASE={db_config['database']};"
    f"UID={db_config['username']};"
    f"PWD={db_config['password']};"
)

# API Key from environment variable
API_KEY = os.getenv('API_KEY', 'simple-api-key-123')  # Set this in Azure

@app.route('/waste_weights', methods=['GET'])
def get_waste_weights():
    api_key = request.headers.get('x-api-key')
    if api_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401

    try:
        # Use context manager for safe connection handling
        with pyodbc.connect(connection_string) as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT waste_class, total_weight FROM waste_weights")
                rows = [{"waste_class": row[0], "total_weight": float(row[1])} for row in cursor.fetchall()]
                return jsonify({"data": rows})
    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Azure App Service uses PORT
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')