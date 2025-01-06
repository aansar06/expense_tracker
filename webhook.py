from flask import Flask

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger():
    # Replace this with the program logic you want to run
    print("Program triggered!")
    # Call your main program logic here
    your_program_logic()
    return "Triggered successfully", 200

def your_program_logic():
    print("Running your program logic!")
    # Add your actual program logic here

if __name__ == '__main__':
    app.run(port=5000)  # Runs the server on http://localhost:5000
