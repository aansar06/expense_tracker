from db_utils import get_counter, reset_counter
import subprocess

def retrain_if_needed():
    count = get_counter()
    if count >= 6:
        print(f"Counter is {count}, retraining model...")
        # Run your actual ML retraining script
        subprocess.run(["python", "retraining_model.py"], check=True)
        # Reset counter after retraining
        reset_counter()
        print("Retraining complete and counter reset.")
    else:
        print(f"Counter is {count}, retraining not needed.")

if __name__ == "__main__":
    retrain_if_needed()
