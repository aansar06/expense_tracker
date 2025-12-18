import subprocess

THRESHOLD = 6

def get_counter():
    try:
        with open("retrain_counter.txt", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def reset_counter():
    with open("retrain_counter.txt", "w") as f:
        f.write("0")

def main():
    count = get_counter()
    print(f"New insertions since last training: {count}")

    if count >= THRESHOLD:
        print("Threshold reached. Retraining model...")
        subprocess.run(["python", "retraining_model.py"], check=True)
        reset_counter()
        print("Retraining complete. Counter reset.")
    else:
        print("Not enough new data. Skipping retraining.")

if __name__ == "__main__":
    main()
