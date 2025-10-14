"""import re
import csv
import gspread
import time

January = {}
February = {}
March = {}
April = {}
May = {}
June = {}
July = {}
August = {}
September = {}
October = {}
November = {}
December = {}
months = [January, February, March, April, May, June, July, August, September, October, November, December]
grocery_stores = ["A & P FOOD STORES", "ALBERTSONS", "ALDI", "ARMANDO'S SUPERMARKET", "AUSTIN FOODS", 
"BASIC AMERICAN FOODS", "BERNER FOODS INCORPORATED", "BUNGE FOODS", "BUTERA FINER FOODS", "C TOWN", 
"CERTIFIED GROCERS OF III", "COSTCO", "COUNTY MARKET", "CUB FOODS", "DAVE'S SUPERMARKET", "DEAN FOODS", 
"DOMINICK'S FINER FOODS", "DOT FOODS", "ECONO FOODS", "FAIRPLAY FINER FOODS", "FAIRWAY FINER FOODS", 
"FAIRWAY FINER FOODS INC.", "FAIRWAY FOODS", "FAMILY FOODS", "FARMLAND FOODS", "FOOD 4 LESS", "FOODLAND", 
"FOODTOWN", "FRIENDLY FOODS", "FRONTERA FOODS", "GUADALAJARA SUPERMARKET", "HANOVER SUPERMARKET", 
"HAPPY FOODS", "HARVEST FOODS", "HOMETOWN FOODS", "JALISCO MARKET", "JEWEL-OSCO", "JIMMY DEAN FOODS", 
"JIMMY FOODS", "JIMMY'S FOODS", "JUBILEE FOODS", "KANESHIC SUPERMARKET", "KEY FOOD", "KING FOOD", 
"KMART SUPER CENTERS", "KROGER", "LOGLI SUPERMARKETS", "MARKET BASKET", "MEIJER", 
"METAL SUPERMARKETS", "NEWLY WEDS FOOD", "NIEMANN FOODS", "PENNANT FOODS", "PEREZ SUPERMARKET", 
"PIGGLY WIGGLY", "PRICE LESS FOODS", "PRICE RITE", "PUBLIX", "RAINBOW FOODS", "SAM'S CLUB", "SAV A LOT", 
"SAVE A LOT", "SAVEWAY FOODS", "SCHNUCK MARKETS", "SCHWAN'S FINE FOOD", "SENTRY FOODS", "SHERWOOD FOODS", 
"SHOP N SAVE", "SHOPRITE", "STOP & SHOP", "SULLIVANS FOODS", "SUNSET FOODS", "SUNSHINE FOODS", 
"SUPER FRESH", "SUPER TARGET", "SUPERVALU", "ULTRA FOOD'S", "ULTRA FOODS", "UNITED SUPERMARKET", 
"WAL-MART SUPERCENTER", "WESTERN SUPERMARKET"]

convinence_stores = ["7-ELEVEN", "MOBIL","MILITO'S", "WALGREENS", 'CIRCLE K' 'CVS', 'BP', 'CITGO']
fast_food = ['BYRDS','BUMPER 2 BURGER', 'NYC HALAL EATS', 'CHI TEA', 'HALAL SMASH BURGER','HELLO SHAWARMA']
categories = []
file  = f"chase_sem1.CSV"

def adjust_date(name, date):
    while(True):
        ind = name.find('/')
        if(ind == -1):
            break
        elif(not name[ind+1].isdigit()):
            name = name[ind+1:]
        else:
            if(date[:4] != name[ind-2:ind+3]):
                date = name[ind-2:ind+3] + date[5:]
            break
    return date

def extract_meaningful_words(name):
    # Remove numbers, dates, state abbreviations, and extra spaces
    meaningful_words = re.sub(r'\b\d+\b|ON|\d{2}/\d{2}|/\s*|EXCHG RTE|Riyal|:', '', name)
    meaningful_words = re.sub(r'\d', '', meaningful_words)
    meaningful_words = re.sub(r'--', '', meaningful_words)

    # Remove extra spaces and return
    return ' '.join(meaningful_words.split())

def add_expense_to_category(category, date, name, amount, tmonth):
    if(category not in tmonth):
        categories.append(category)
        tmonth[category] = []
    tmonth[category].append([date, name, amount])


sa = gspread.service_account(filename="credentials/service_account.json")
sh = sa.open("Personal Finances(2024-25)")
with open(file, mode = 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for row in csv_reader:
        
        date = row[1]
        name = row[2]
        amount = row[3]
        if(name[:5] != 'Zelle'):
            date = adjust_date(name, date)
                
        temp_month = months[int(date.split("/")[0])-1]
        if(name[:4] == 'TEAM'):
            add_expense_to_category("Physical Therapy", date, 'TEAM REHAB', amount, temp_month)
            continue
        elif(name[17:21] == "Zaki" and amount == '-30.00'):
            add_expense_to_category("Phone Bill", date, 'Zelle Payment To Zaki', amount, temp_month)
            continue
        elif(name[17:22] == 'Jawad' or name[17:21] == 'Zaki'):
            add_expense_to_category("Personal Expenses", date, 'Zelle Payment to ' + name[17:22].strip(), amount, temp_month)
            continue
        elif(name.split(" ")[0] in grocery_stores):
            add_expense_to_category("Grocery Stores", date, name.split(" ")[0], amount, temp_month)
            continue
        elif(name.split(" ")[0] in convinence_stores):
            add_expense_to_category("Convinences/Snacks", date, name.split(" ")[0], amount, temp_month) 
            continue
        elif(name[:3] == 'EEH'):
            add_expense_to_category("Medical Expenses", date, 'Edward Health', amount, temp_month)
            continue
        elif(name.split(" ")[2] == "MEDITERRANEA"):
            add_expense_to_category("Meat", date, 'Mediterranea', amount, temp_month)
            continue
        elif(name[17:30] == "Abdullah Raza"):
            add_expense_to_category("807 Wifi", date, 'Zelle Payment to Abdullah Raza', amount, temp_month)
            continue
        elif(name[:8] == 'COINBASE'):
            add_expense_to_category("Crypto", date, 'COINBASE', amount, temp_month)
            
            continue
        elif(amount[0] != '-'):
            add_expense_to_category("Gains", date, name, amount, temp_month)
            continue
        elif('Zaid' in name):
            add_expense_to_category("Fast Food", date, 'Zelle Payment to Zaid Raza', amount, temp_month)
            continue
        
        if(name.startswith("TST*")):
            name = name[4:]
            for chain in fast_food:
                if(chain in name):
                    add_expense_to_category("Fast Food", date, chain, amount, temp_month)
                    break
            continue
        
        name = extract_meaningful_words(name)
        add_expense_to_category("Shopping", date, name, amount, temp_month)


def print_total(row, col, total):
    wks.update_cell(row, col, "Total")
    time.sleep(2)
    wks.update_cell(row, col+2, f"${total}")
    time.sleep(2)

def print_income(total):
    wks.update_cell(2, 2, f"${total}")
    time.sleep(2)


def print_expense(loss):
    wks.update_cell(3, 2, f"${loss}")
    time.sleep(2)

month = 0
for dict in months:
    if(dict):
        wks = sh.worksheet(month_names[month])
        wks.batch_clear(['A7:C100'])
        
        start_column_category = 1
        start_row_category = 8
        start_row_expense = 9
        loss = 0
        
        for category in dict:
            wks.update_cell(start_row_category, start_column_category, category)
            time.sleep(2)
            total = 0
        
            for expense in dict[category]:
                wks.insert_row(expense, start_row_expense)
                total+=float(expense[2])
                time.sleep(2)
                start_row_expense+=1
        
            print_total(start_row_expense, start_column_category, total)
            
            if(total>=0):
                print_income(total)
            else:
                loss+= total

            start_row_category = start_row_expense + 2
            start_row_expense+=3
        
        print_expense(loss)
    month+=1
"""
months_map = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}