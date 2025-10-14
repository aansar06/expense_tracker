import expenses_bank
import gspread
import joblib
import pandas as pd
import sqlite3
import subprocess
from datetime import datetime


"""def retrain_model():
    subprocess.run(["python", "retraining_model.py"], check=True)
    print("✅ Model retrained with new data")"""

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
    return email_text[start_ind:end_ind]

    

def get_name(email_text):
    '''
    O(1) time for start_ind since "with " is always at the same place
    O(m) time for end_ind where m is the length of the name since .find() starts from start_ind(beginning of name)
    O(m) for slicing the string to get the name
    Overall O(1+m+m) = O(m) time complexity where m is the length of the name

    '''
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
    start_index = email_text.find("Made on ")+8

    # getting month, day, year
    month = email_text[start_index:start_index+3]
    day = email_text[start_index+4:start_index+6]
    year = email_text[start_index+8:start_index+12]
    
    # using dictionary to get month number: O(1) ammortized time
    month_number = expenses_bank.months_map[month]

    # formatting date as MM/DD/YYYY
    date = f"{month_number}/{day}/{year}"

    return date

def get_category(name):

    # preprocessing the name
    name = name.lower().strip()

    # predicting the category
    X_new = pd.Series([name])
    predicted_category = model.predict(X_new)[0] 

    # getting confidence
    proba = model.predict_proba(X_new)
    confidence = proba.max() 

    # if(confidence < 0.6):
    #     # check if name is in backup database
    #     conn = sqlite3.connect('intro.db')
    #     cursor = conn.cursor()
    #     cursor.execute("""
    #         SELECT merchant_category
    #         FROM backup_data
    #         WHERE LOWER(?) LIKE '%' || LOWER(merchant) || '%' LIMIT 1 """, (name,)
    #     )

    #     # get the name of the category
    #     row = cursor.fetchone()
    #     if row:
    #         predicted_category = row[0]
    #         cursor.execute(""" 
    #             INSERT INTO training_dataset (merchant_category, merchant)
    #             VALUES (?, ?) 
    #             """, (predicted_category, name)
    #         )
    #         cursor.execute(""" 
    #             INSERT INTO training_dataset (merchant_category, merchant)
    #             VALUES (?, ?) 
    #             """, (predicted_category, name)
    #         )
    #         conn.commit()
    #         conn.close()
    #         # retrain the model
    #         #retrain_model()
    #     else:
    #         predicted_category = "Other"
    #         cursor.execute(""" 
    #             INSERT INTO corrections (merchant_category, merchant)
    #             VALUES (?, ?) 
    #             """, (predicted_category, name)
    #         )

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

            
def parse_email(email_text):
    name = get_name(email_text)
    amount = get_amount(email_text)
    date = get_date(email_text)
    category = get_category(name)
    add_expense_to_sheet(date, name, amount, category)



    
