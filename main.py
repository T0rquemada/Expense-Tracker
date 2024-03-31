import re
import sqlite3
from datetime import datetime


def show__menu():
    print('1. Add expense')
    print('2. Add income')
    print('3. Expense statistic')
    print('4. Income statistic')


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


def get_current_month():
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


def add_note(current_month, note_type, cursor):
    table_name = f'{current_month}_{note_type}'
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

    create__table(cursor, table_name)

    if is__category__exist(cursor, note_category, table_name):
        old_value = get_amount_from_column(cursor, note_category, table_name)
        new_value = old_value + note_amount
        update_value(cursor, note_category, new_value, table_name)
    else:
        queue = f"INSERT INTO {table_name} (category, amount) VALUES (?, ?)"
        cursor.execute(queue, (note_category, note_amount))


# Return all month, depending on type (expense or income)
def get_all_month(table_type, cursor):

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    filtered_names = [s for s in table_names if f'_{table_type}' in s]

    return filtered_names


def show_stat(table_type, cursor, stat_type):
    months = get_all_month(table_type, cursor)

    # Show stat for month
    if stat_type == 'month':
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

    # Show stat for year
    elif stat_type == 'year':
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

    if usr_option == '1':
        show_stat(note_type, cur, 'month')
    elif usr_option == '2':
        show_stat(note_type, cur, 'year')
    else:
        print('Incorrect input')
        return 1


def main():
    show__menu()
    user__input = input('Choose option (contain only number): ')

    if has_not_nums(user__input):
        while True:
            user__input = input('Incorrect input, choose option: ')
            if not has_not_nums(user__input):
                break

    current_month = get_current_month() + str(datetime.now().year)  # Defining current month with year
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    if user__input == '1':  # Add expense
        add_note(current_month, 'expense', cursor)
    elif user__input == '2':    # Add income
        add_note(current_month, 'income', cursor)
    elif user__input == '3':    # Expense statistic
        statistics_section('expense', cursor)
    elif user__input == '4':    # Income statistic
        statistics_section('income', cursor)
    else:
        print('Incorrect input')
        return 1

    connection.commit()
    cursor.close()
    connection.close()

    return 0


main()
