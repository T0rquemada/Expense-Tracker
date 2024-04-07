import re
import os
import sqlite3
import csv
from datetime import datetime


def show__menu():
    print('1. Add expense')
    print('2. Add income')
    print('3. Expense statistic')
    print('4. Income statistic')
    print('5. Load notes from bank report')


# Return true, if 'text' has not nums
def has_not_nums(text):
    if isinstance(text, str):   # Works only if text is string
        nums = r'^-?\d+\.?\d*$'
        if re.match(nums, text):
            return False
        else:
            return True
    else:
        return None


# If user input not number, starts infinity while loop
def check_usr_input(user__input):
    if has_not_nums(user__input):
        while True:
            user__input = input('Incorrect input, choose option: ')
            if not has_not_nums(user__input):
                break


def get_current_month(current_data=0):
    if current_data == 0:
        current_data = datetime.now().month

    if current_data == 1:
        current_data = 'January'
    if current_data == 2:
        current_data = 'February'
    if current_data == 3:
        current_data = 'March'
    if current_data == 4:
        current_data = 'April'
    if current_data == 5:
        current_data = 'May'
    if current_data == 6:
        current_data = 'June'
    if current_data == 7:
        current_data = 'July'
    if current_data == 8:
        current_data = 'August'
    if current_data == 9:
        current_data = 'September'
    if current_data == 10:
        current_data = 'October'
    if current_data == 11:
        current_data = 'November'
    if current_data == 12:
        current_data = 'December'

    return current_data


def create__table(cur, table_name):
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        category TEXT NOT NULL,
                        amount INT NOT NULL
                    )''')


# If category already exist in db, return True, if not - False
def is__category__exist(cur, category, table_name):
    cur.execute(f"SELECT * FROM {table_name} WHERE category=?", (category,))
    row = cur.fetchone()

    if row is not None:
        return True

    return False


def get_amount_from_column(cur, category, table_name):
    cur.execute(f"SELECT amount FROM {table_name} WHERE category=?", (category,))
    row = cur.fetchone()
    return row[0]


def update_value(cur, category, expense_sum, table_name):
    cur.execute(f"UPDATE {table_name} SET amount = ? WHERE category = ?", (expense_sum, category,))


def add_note(cursor, note_data, note_category, note_amount, note_type):
    table_name = f'{note_data}_{note_type}'
    create__table(cursor, table_name)

    if is__category__exist(cursor, note_category, table_name):
        old_value = get_amount_from_column(cursor, note_category, table_name)
        new_value = old_value + note_amount
        update_value(cursor, note_category, new_value, table_name)
    else:
        queue = f"INSERT INTO {table_name} (category, amount) VALUES (?, ?)"
        cursor.execute(queue, (note_category, note_amount))


def add_note_section(current_data, note_type, cursor):
    note = input(f'Enter {note_type} amount and category, divided by space: ')

    try:
        if ' ' in note:
            note_amount = int(note[:note.index(' ')])
            note_category = note[note.index(' ') + 1:]
        else:
            note_amount = int(note)
            note_category = 'No category'

        note_amount = abs(note_amount)
    except ValueError as error:
        print('Error while catch user input for income:  ', error)
        return 1

    add_note(cursor, current_data, note_category, note_amount, note_type)


# Return all month, depending on type (expense or income)
def get_all_month(table_type, cursor):

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    filtered_names = [s for s in table_names if f'_{table_type}' in s]

    return filtered_names


def show_stat(table_type, cursor, stat_type):
    months = get_all_month(table_type, cursor)

    if stat_type == 'month':    # Show stat for month
        for month in months:
            print(month[:month.index('_')])

        month_choose = input('Choose month, enter full title: ') + '_' + table_type
        print('\n')
        try:
            cursor.execute(f"SELECT * FROM {month_choose} ORDER BY amount DESC")
        except sqlite3.OperationalError as error:
            print('Error reading table: ', error)
            return 1

        data = cursor.fetchall()

        print('Expenses from ', month_choose[:month_choose.index('_')])
        total = 0
        for expense in data:
            total += expense[2]
            print(expense[1], ':', expense[2], 'UAH')

        print('\n')
        print('Total: ', total, 'UAH')

    elif stat_type == 'year':   # Show stat for year
        years = []

        for month in months:
            year = month[month.index('2'):month.index('_')]
            if year not in years:
                years.append(year)
                print(month[month.index('2'):month.index('_')])

        year_choose = input('Choose year: ')
        print('\n')

        if year_choose in years:
            notes = {}
            total = 0

            filtered_month = [s for s in months if f'{year_choose}' in s]
            for month in filtered_month:
                cursor.execute(f"SELECT * FROM {month} ORDER BY amount DESC")
                data = cursor.fetchall()
                for note in data:
                    total += note[2]
                    if note[1] in notes.keys():
                        notes[note[1]] += note[2]
                    else:
                        notes[note[1]] = note[2]

            for key, value in notes.items():
                print(key, ': ', value)

            print('\n')
            print('Total: ', total)
        else:
            print('Year not find')
            return 1


def statistics_section(note_type, cur):
    print(f'1. Month {note_type} statistic')
    print(f'2. Year {note_type} statistic')
    usr_option = input('Choose option: ')

    check_usr_input(usr_option)

    if usr_option == '1':
        show_stat(note_type, cur, 'month')
    elif usr_option == '2':
        show_stat(note_type, cur, 'year')
    else:
        print('Incorrect input')
        return 1


def read_csv(file_name):
    with open(file_name, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)    # Skip first line in file

        data = [[row[0][3:10], row[1], row[3]] for row in reader if float(row[3]) < 0]

        return data


def specify_category(input_category):
    food = ['АТБ', 'ATB 113', 'VARUS', 'Moeselo', 'Сільпо']
    coffee = ['Франс.уа', 'Bulochnik']
    mails = ['Укрпошта']
    healthcare = ['EVA']
    shop = ['AliExpress', 'Списання AliExpress', 'Аврора', 'Avrora Multimarket', 'Ашан', 'UAPAY']
    fast_food = ['Europa', 'FutKort', 'MAVRA PIZZA', 'McDonald’s']
    gadgets = ['Vodafone', 'Comfy']

    transfers_to_card = r'^\d{6}\*{4}\d{4}$'
    ignored_categories = ['Округлення балансу']

    if input_category in food:
        return 'Food'
    elif re.match(transfers_to_card, input_category):
        return 'Transfers to card'
    elif input_category in fast_food:
        return 'Fast food'
    elif input_category in gadgets or gadgets[0] in input_category:
        return 'Gadgets'
    elif input_category in coffee:
        return 'Coffee'
    elif input_category in healthcare:
        return 'Healthcare'
    elif input_category in shop:
        return 'Shop'
    elif input_category in mails:
        return 'Mail'
    elif input_category in ignored_categories or ignored_categories[0] in input_category:
        return None
    else:
        return input_category


def filter_csv_data(notes):
    filtered_data = []
    for row in notes:
        data = get_current_month(int(row[0][:2])) + row[0][3:]
        category = specify_category(row[1])
        amount = float(row[2])
        filtered_row = [data, category, abs(round(amount))]
        if category is not None:
            filtered_data.append(filtered_row)

    return filtered_data


# Return all files with defined extension
def find_bank_reports(extension):
    reports = []
    for filename in os.listdir('reports/'):
        if filename.endswith(extension):
            reports.append(filename)

    return reports


def delete_reports(reports):
    for report in reports:
        try:
            os.remove(os.path.join('reports/', report))
        except Exception as e:
            print(f"Error deleting file '{report}': {e}")


# For monobank reports in .csv
def load_from_csv(cursor, check_reports):
    reports = find_bank_reports('.csv')

    check_reports(reports)

    try:
        for report in reports:
            data = read_csv("reports/" + report)
            filtered_data = filter_csv_data(data)

            for note in filtered_data:
                add_note(cursor, *note, 'expense')

        delete_reports(reports)
    except Exception as e:
        print('Something get wrong with load data from .csv: ', e)
        return 1


def load_section(cursor):
    def check_reports(reports):
        if not reports:
            print("No bank reports founded")
            return 1

    print('1. Monobank (.csv)')

    usr_choice = input('Enter your choice: ')
    check_usr_input(usr_choice)

    if usr_choice == '1':
        load_from_csv(cursor, check_reports)
    else:
        print('Incorrect input')
        return 1


def main():
    show__menu()
    user__input = input('Choose option (contain only number): ')

    check_usr_input(user__input)

    current_data = get_current_month() + str(datetime.now().year)  # Defining current month with year
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    if user__input == '1':  # Add expense
        add_note_section(current_data, 'expense', cursor)
    elif user__input == '2':    # Add income
        add_note_section(current_data, 'income', cursor)
    elif user__input == '3':    # Expense statistic
        statistics_section('expense', cursor)
    elif user__input == '4':    # Income statistic
        statistics_section('income', cursor)
    elif user__input == '5':    # Load data from reports
        load_section(cursor)
    else:
        print('Incorrect input')
        return 1

    connection.commit()
    cursor.close()
    connection.close()

    return 0


main()

# Statistics if expense/income null
# load from report if reports not finded
