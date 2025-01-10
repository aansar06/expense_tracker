import expenses_bank
import gspread
import time
def get_amount(email_text):
    dollar_index  = email_text.find("$")
    amount = ('-'+email_text[dollar_index+1:dollar_index+6])
    return amount

def get_name(email_text):
    start_index = email_text.find("You sent a payment to ")+22
    end_index = email_text.find('\n', start_index)
    name = email_text[start_index:end_index]
    return name

def get_date(email_text):
    start_index = email_text.find("Sent on ")+8
    end_index = email_text.find("\n", start_index)
    #getting date in the form of Month Day, Year
    date = email_text[start_index:end_index]
    
    #converting date to the form of MM/DD/YYYY
    date.split(" ")
    for month in expenses_bank.month_names:
        if(date[0].lower() == month[:3]):
            month_number = f"{expenses_bank.month_names.index(month) + 1:02}"
            break
    day = date[1].replace(",", "")
    year = date[2]
    date = f"{month_number}/{day}/{year}"
    return date


def add_expense_to_sheet(date, name, amount, category, mnth):
    sa = gspread.service_account()
    sh = sa.open("Personal Finances(2024-25)")
    wks = sh.worksheet(expenses_bank.month_names[mnth-1])

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
    if("You sent a Zelle® payment" in email_text):
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


    
