from flask import Flask, request, jsonify
import os
import add_single_expense
ee
app = Flask(__name__)

EXPECTED = os.environ.get('API_KEY')

@app.route('/trigger', methods=['POST'])
def trigger():
    
    auth = request.headers.get('Authorization')
    
    if not auth or auth != f"Bearer {EXPECTED}":
        return jsonify({"message": "Unauthorized", "status": 401}), 401
    
    # Get the email body from the incoming JSON request
    data = request.get_json()  # This will parse the JSON body into a Python dictionary
    
    if data and 'email_body' in data:
        email_text = data['email_body']
       
        # Call your main program logic with the email text if needed
        your_program_logic(email_text)
        return jsonify({"message": "Triggered successfully", "status": 200}), 200
    else:
        return jsonify({"message": "No email body found", "status": 400}), 400

def your_program_logic(email_text):
    # Here you can process the email_text as needed
    print("Running your program logic with the email content:")
    # Process or manipulate email text as needed
    add_single_expense.parse_email(email_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

