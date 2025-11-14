import expenses_bank
import gspread
import joblib
import pandas as pd
import sqlite3
import subprocess
from datetime import datetime
import re


def retrain_model():
    print("♻️  Retraining model (every 6 insertions)...")
    subprocess.run(["python", "retraining_model.py"], check=True)
    print("✅ Model retrained!")

# loading the trained model
model = joblib.load("merchant_model.pkl")

def get_wks(date_str):
    sa = gspread.service_account(filename="credentials/service_account.json")
    sh = sa.open("Personal Finances(2024-25)")
    dt = datetime.strptime(date_str, "%m/%d/%Y")
    month_name = dt.strftime("%B")
    wks = sh.worksheet(month_name.lower())
    return wks


def get_amount(email_text):
    '''
    O(1) time for start_ind since "$" is always at the same place
    O(a) time for end_ind where a is the length of the amount(i.e; 14.00 has length = 5) since we are iterating through each character until we find a space
    O(a) for slicing the string to get the amount
    Overall O(1+a+a) = O(a) time complexity where a is the length of the amount
    
    * Runtime is near O(1) since 'a' only differs by a couple characters in length (max length of amount can be 7-8)

    '''
    # start_ind is the index of the first character of the amount
    start_ind = email_text.find("$")+1
    end_ind = start_ind
    # iterating through each character until we find a space
    while email_text[end_ind] != " ":
        end_ind += 1 # end_ind is the index of the last character after the amount

    # slicing the string to get the amount
    amount = email_text[start_ind:end_ind]

    #converting amount to float and negative value for expense
    if("You made" in email_text or "You sent" in email_text):
        print("Transaction indicates an expense")
        amount = float(amount) * -1
    elif("sent you" in email_text):
        print("Transaction indicates a gain")
        amount = float(amount)
    
    return amount

    

def get_name(email_text):
    '''
    O(1) time for start_ind since "with " is always at the same place
    O(m) time for end_ind where m is the length of the name since .find() starts from start_ind(beginning of name)
    O(m) for slicing the string to get the name
    Overall O(1+m+m) = O(m) time complexity where m is the length of the name

    '''

    if(email_text.startswith("Zelle") and "sent you" in email_text):
        # getting the name of sender
        name = email_text[email_text.find("payment ")+8:email_text.find("sent")]

        # getting the description
        start = email_text.find("Memo ")+5 # start index of the description
        description = email_text[start:email_text.find(name, start)] # slicing the string to get the description
        return f"{name}: {description}"
        
    elif(email_text.startswith("Zelle") and "you sent" in email_text):
        name = email_text[email_text.find("to ")+3:email_text.find("Here")]
        start = email_text.find("Memo ")+5 # start index of the description
        description = email_text[start:email_text.find(name, start)] # slicing the string to get the description
        return f"{name}: {description}"

    else:

        # start_ind is the index of the first character of the name
        start_ind_n = email_text.find("with ")+5
        # end_ind is the index of the last character after the name
        end_ind_n = email_text.find("Account", start_ind_n)
        # slicing the string to get the name
    return email_text[start_ind_n:end_ind_n]

def get_date(email_text):
    '''
    O(c) time for start_index where c is the number of characters before "Made on "
    O(1) time for month, day, year since they are always at the same place after start_index
      - months_map is a dictionary so getting the month number is O(1) ammortized
    Overall O(1+c) = O(c) time complexity where m is the number of characters before "Made on "

    * Runtime is near O(1) since 'm' is roughly the same in practical cases

    '''
    # start_index is the index of the first character of the month
    if(email_text.startswith("Zelle")):
        start_index = email_text.find("Sent on ")+8
    else:
        start_index = email_text.find("Made on ")+8

    # getting month, day, year
    month = email_text[start_index:start_index+3]
    day = email_text[start_index+4:start_index+6].replace(',', '')
    if(len(day) == 1):
        year = email_text[start_index+7:start_index+11]
    else:
        year = email_text[start_index+8:start_index+12]
    day = day.zfill(2)  # padding day with leading zero if needed
    
    # using dictionary to get month number: O(1) ammortized time
    month_number = expenses_bank.months_map[month]

    # formatting date as MM/DD/YYYY
    date = f"{month_number}/{day}/{year}"

    return date

def get_category(name):

    # preprocessing the name
    name = name.lower().strip()
    name = re.sub(r'\.com|\.net|\.org|\.co|\.in|\.ca|\.uk', '', name)

    # predicting the category
    X_new = pd.Series([name])
    predicted_category = model.predict(X_new)[0] 

    # getting confidence
    proba = model.predict_proba(X_new)
    confidence = proba.max() 
    print(confidence)
    if(confidence < 0.6):
        # check if name is in backup database
        print("confidence is less than 60%")
        conn = sqlite3.connect('intro.db')
        cursor = conn.cursor()
        # checks if merchant in backup database is a substring of the name dervied from email
        cursor.execute("""
            SELECT merchant_category
            FROM backup_data
            WHERE LOWER(?) LIKE '%' || LOWER(merchant) || '%' LIMIT 1 """, (name,)
        )

        # get the name of the category
        row = cursor.fetchone()
        if row:
            predicted_category = row[0]
            cursor.execute(""" 
                INSERT INTO training_dataset (merchant_category, merchant)
                VALUES (?, ?) 
                """, (predicted_category, name)
            )
            cursor.execute(""" 
                INSERT INTO training_dataset (merchant_category, merchant)
                VALUES (?, ?) 
                """, (predicted_category, name)
            )
            conn.commit()
            print("USED BACKUP DATABASE")
            print("inserted new data into training dataset")

            # ✅ Check how many rows exist in training_dataset
            cursor.execute("SELECT COUNT(*) FROM training_dataset")
            count = cursor.fetchone()[0]
            print(f"training_dataset row count: {count}")

            # ✅ Retrain every 6 insertions
            if count % 6 == 0:
                print("♻️  Retraining model (every 6 insertions)...")
                subprocess.run(["python", "retraining_model.py"], check=True)
                print("✅ Model retrained!")
            
            
        else:
            predicted_category = "Other"
            print("data not found in backup database, assigned to Other category")
            print("inserting data into corrections table for manual review")
            cursor.execute(""" 
                INSERT INTO corrections (merchant_category, merchant)
                VALUES (?, ?) 
                """, (predicted_category, name)
            )
            conn.commit()
        conn.close()
    else:
        print("confidence is greater than 60%")
    return predicted_category


def add_expense_to_sheet(date, name, amount, category):
    """
    Adds an expense entry to the given month's worksheet.
    If the category exists, inserts the expense below it.
    If not, creates the category and inserts it at the end.
    """
    wks = get_wks(date)
    category = category.strip()
    word_to_search = category

    # Get all values in the first column starting from row 8
    category_col = wks.col_values(1)[7:]  # zero-indexed, so skip first 7 rows
    base_row = 8  # actual first row in the sheet to start looking

    found_row = None

    # Search for category name
    for i, cell_value in enumerate(category_col, start=base_row):
        if cell_value and word_to_search.lower() in cell_value.lower():
            found_row = i
            break

    if found_row:
        # Insert expense just below the category
        insert_row = found_row + 1
        wks.insert_row([date, name, amount], insert_row)
        print(f"✅ Added expense under existing category '{category}' at row {insert_row}.")
    else:
        # Append new category and expense at the end
        last_row = len(category_col) + base_row
        wks.update_cell(last_row + 1, 1, word_to_search)
        wks.insert_row([date, name, amount], last_row + 2)
        print(f"🆕 Created new category '{category}' and added expense below it.")
    
    # Update the total for the category
    for i, cell_value in enumerate(category_col[found_row:], start=found_row+1):
        if not cell_value.strip():     
            # Update the cell that's empty with the word "Total"
            wks.update_cell(i, 1, "Total")
            break
        elif cell_value.strip() == "Total":
            # the cell contains "Total", so we break the loop to add the total in this row
            break
        
        # update the total for this specific category in which expense was added
        update_category_total(i, amount, wks)

    # Update overall income or expenses
    if float(amount)< 0:
        update_expenses(amount, wks)
    else:
        update_income(amount, wks)


def update_category_total(found_row, amount, wks):

    # get the current total from column 3 of the found_row
    current_total = wks.cell(found_row, 3).value or "0"

    # update the total by adding the amount of the expense to the current total
    new_total = float(current_total.replace("$", "").replace(",", "")) + amount

    # formats the total as $xx if positive, or -$xx if negative
    wks.update_cell(found_row, 3, "${:,.2f}".format(new_total).replace("$-", "-$"))

def update_income(amount, wks):
    # get the current income of the month
    current_income = wks.cell(2, 2).value or "0"

    # update the income by adding the amount to the current income
    new_income = float(current_income.replace("$", "").replace(",", "")) + amount

    # formats the income as $xx
    wks.update_cell(2, 2, "${:,.2f}".format(new_income))

def update_expenses(amount, wks):
    # get the current total expenses of the month
    current_expenses = wks.cell(3, 2).value or "0"

    # update the total expenses by adding the amount to the current expenses
    new_expenses = float(current_expenses.replace("$", "").replace(",", "")) + amount

    # formats the expenses as -$xx
    wks.update_cell(3, 2, "${:,.2f}".format(new_expenses).replace("$-", "-$"))

def parse_email(email_text):
    name = get_name(email_text)
    amount = get_amount(email_text)
    date = get_date(email_text)
    if "sent you" in email_text:
        print("This is an incoming transaction. No expense to add.")
        category = "Income"
    else:
        category = get_category(name)
    add_expense_to_sheet(date, name, amount, category)
    print(f"Added the following expense to the sheet: {name}, ${amount}, {date}, {category}")

if __name__ == "__main__":
    # Example email text
    email_text = "Transaction alert You made a debit card transaction of $6.69 with TST* DOG HAUS BIERGA Account ending in (...0364) Made on Sep 30, 2025 at 2:13 AM ET Description TST* DOG HAUS BIERGA Amount $6.69 You"
    parse_email(email_text)

    
