from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Fetch the API key from environment variables
API_KEY = os.getenv("API_KEY")

@app.route('/trigger', methods=['POST'])
def trigger():
    # Check if the correct API key is provided in the request headers
    client_api_key = request.headers.get('X-API-KEY')
    
    if client_api_key != API_KEY:
        # If the API key doesn't match, return an unauthorized response
        return jsonify({"error": "Unauthorized"}), 403

    # If the API key is correct, proceed with your program logic
    print("Program triggered!")
    # Call your main program logic here
    your_program_logic()
    return "Triggered successfully", 200

def your_program_logic():
    print("Running your program logic!")
    # Your program logic here (what happens after the trigger is called)

if __name__ == '__main__':
    app.run(debug=False, port=5000)  # Change port if necessary
