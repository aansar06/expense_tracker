import expenses_bank
import gspread
import time
import joblib
import pandas as pd
import sqlite3
import subprocess


def retrain_model():
    subprocess.run(["python", "retraining_model.py"], check=True)
    print("✅ Model retrained with new data")

def get_wks(month):
    sa = gspread.service_account(filename="credentials/service_account.json")
    sh = sa.open("Personal Finances(2024-25)")
    wks = sh.worksheet(expenses_bank.month_names[month-1])
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
    # loading the trained model
    model = joblib.load("merchant_model.pkl")

    # preprocessing the name
    name = name.lower().strip()

    # predicting the category
    X_new = pd.Series([name])
    predicted_category = model.predict(X_new)[0] 

    # getting confidence
    proba = model.predict_proba(X_new)
    confidence = proba.max() 

    if(confidence < 0.6):
        # check if name is in backup database
        conn = sqlite3.connect('intro.db')
        cursor = conn.cursor()
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
            # retrain the model
            retrain_model()
        else:
            predicted_category = "Other"
            cursor.execute(""" 
                INSERT INTO corrections (merchant_category, merchant)
                VALUES (?, ?) 
                """, (predicted_category, name)
            )

    return predicted_category


def add_expense_to_sheet(date, name, amount, category, mnth):
    wks = get_wks(mnth)
    

    # Search for the word "gain" in the first column starting from row 8
    word_to_search = category
    for row in range(8, wks.row_count + 1):
        #getting the value of the cell in column 1
        cell_value = wks.cell(row, 1).value
        
        #if the cell is not empty
        if cell_value:
            #if the word is found in the cell
            if(word_to_search in cell_value):
                # insert expense in 'next cell'
                wks.insert_row([date, name, amount], row+1)
                time.sleep(2)
                break
            else:
                continue
        
        #if the cell is empty
        else:
            #if the 'next cell' is empty
            if not wks.cell(row+1, 1).value:
                # insert name of category in 'next cell'
                wks.update_cell(row+1, 1, word_to_search)
                time.sleep(2)
                # insert expense in 'next next cell'
                wks.insert_row([date, name, amount], row+2)
                time.sleep(2)
                break
            
            # if the next cell is not empty, do nothing
            
def parse_email(email_text):
    '''if("You sent a Zelle® payment" in email_text):
        amount = get_amount(email_text)
        name = get_name(email_text)
        date = get_date(email_text)
        month_number = int(date.split("/")[0])
        temp_month = expenses_bank.months[month_number-1]
        if(name == 'Zaki Ansari' and amount == '-30.00'):
            expenses_bank.add_expense_to_category("Phone Bill", date, f"Zelle Payment to {name.split(' ')[0]}", amount, temp_month)
            add_expense_to_sheet(date, name, amount, "Phone Bill", month_number)
        elif(name == 'Jawad Ansari' or name == 'Zaki Ansari'):
            expenses_bank.add_expense_to_category("Personal Expenses", date, f"Zelle Payment to {name.split(' ')[0]}", amount, temp_month)
            add_expense_to_sheet(date, name, amount, "Personal Expenses", month_number)
        else:
            expenses_bank.add_expense_to_category("807 Wifi", date, f"Zelle Payment to {name}", amount, temp_month)
            add_expense_to_sheet(date, name, amount, "807 Wifi", month_number)
    else:
        return False'''
    name = get_name(email_text)
    amount = get_amount(email_text)
    date = get_date(email_text)
    category = get_category(name)



    
