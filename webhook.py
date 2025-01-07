from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger():
    # Get the email body from the incoming JSON request
    data = request.get_json()  # This will parse the JSON body into a Python dictionary
    
    if data and 'email_body' in data:
        email_text = data['email_body']
        print("Received email content: ", email_text)
        # Call your main program logic with the email text if needed
        your_program_logic(email_text)
        return jsonify({"message": "Triggered successfully", "status": 200}), 200
    else:
        return jsonify({"message": "No email body found", "status": 400}), 400

def your_program_logic(email_text):
    # Here you can process the email_text as needed
    print("Running your program logic with the email content:")
    print(email_text)  # Process or manipulate email text as needed

if __name__ == '__main__':
    app.run(port=5000)  # Runs the server on http://localhost:5000
