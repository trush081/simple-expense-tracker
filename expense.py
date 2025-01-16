import csv
import time
import sqlite3
import matplotlib.pyplot as plt

# expense.py
# Author: Trent Rush
# Created: 2025-01-16
# Description: Learning Python in Depth - Simple expense tracker
# Usage:
#   1. Run the script using the command: python expense.py
#   2. Follow the on-screen prompts to add expenses, view summaries, export data, and update budgets.
# Requirements:
#   - Python 3.x
#   - sqlite3
#   - matplotlib

def init_db():
    """Initialize the database and create tables if they do not exist."""
    conn = sqlite3.connect('expenses.db')
    create_users_table(conn)
    create_expenses_table(conn)
    return conn

def create_users_table(conn):
    """Create the users table if it does not exist."""
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                budget REAL DEFAULT 0
            )
        ''')

def create_expenses_table(conn):
    """Create the expenses table if it does not exist."""
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

def show_menu():
    """Display the main menu options."""
    print("")
    print("---------------------------------")
    print("Choose an option:")
    print("1. Add a new expense")
    print("2. View expense summary")
    print("3. Export expenses to file")
    print("4. Update budget")
    print("5. Exit")
    print("---------------------------------")
    print("")

def add_expense(conn, user_id):
    """Prompt the user to add a new expense and insert it into the database."""
    description = input('Enter description: ')
    amount = float(input('Enter amount: '))
    category = input('Enter category: ')
    date = input('Enter date (optional, format YYYY-MM-DD): ')
    if not date:
        date = time.strftime('%Y-%m-%d')

    with conn:
        conn.execute('''
            INSERT INTO expenses (description, amount, category, date, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (description, amount, category, date, user_id))

        print("Expense added successfully!")

        check_budget(conn, user_id)

def fetch_expenses(conn, user_id):
    """Fetch all expenses for a given user from the database."""
    with conn:
        cursor = conn.execute('SELECT description, amount, category, date FROM expenses WHERE user_id = ?', (user_id,))
        expenses = cursor.fetchall()
        return [{"description": row[0], "amount": row[1], "category": row[2], "date": row[3]} for row in expenses]

def generate_expense_bar_chart(categories, expenses):
    """Generate and display a bar chart of expenses by category."""
    plt.bar(categories, expenses)
    plt.title('Monthly Expenses')
    plt.xlabel('Category')
    plt.ylabel('Amount ($)')
    plt.show()

def view_expense_summary(conn, user_id):
    """Display a summary of expenses and generate a bar chart."""
    expenses = fetch_expenses(conn, user_id)

    if len(expenses) == 0:
        print("No expenses found.")
        return

    total = sum(expense['amount'] for expense in expenses)

    # Calculate total expenses for each category
    category_total = {}
    for expense in expenses:
        category = expense['category']
        if category in category_total:
            category_total[category] += expense['amount']
        else:
            category_total[category] = expense['amount']

    budget = get_budget(conn, user_id)

    print("Budget: $", budget)
    print("Total expenses: $", total)
    print("Category-wise expenses:")
    for category, amount in category_total.items():
        print(f"  {category}: ${amount:.2f}")

    generate_expense_bar_chart(category_total.keys(), category_total.values())

def export_expenses(conn, user_id):
    """Export all expenses for a given user to a CSV file."""
    expenses = fetch_expenses(conn, user_id)

    filename = f'expenses-{user_id}.csv'
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['description', 'amount', 'category', 'date'])
        writer.writeheader()
        writer.writerows(expenses)
    print(f"Expenses exported to {filename} successfully!")

def fetch_or_create_user_id(conn, username):
    """Fetch the user ID for a given username, or create a new user if not found."""
    username = username.lower().strip()
    with conn:
        cursor = conn.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user is None:
            cursor = conn.execute('''
                INSERT INTO users (username)
                VALUES (?)
            ''', (username,))
            return cursor.lastrowid
        else:
            return user[0]

def get_budget(conn, user_id):
    """Fetch the budget for a given user."""
    with conn:
        cursor = conn.execute('SELECT budget FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()[0]

def check_budget(conn, user_id):
    """Check if the total expenses exceed the budget and display a warning if so."""
    budget = get_budget(conn, user_id)
    expenses = fetch_expenses(conn, user_id)

    if len(expenses) == 0:
        print("No expenses found.")
        return

    total = sum(expense['amount'] for expense in expenses)

    if total > budget:
        print("Budget Exceeded!!!")
    print("Total Expenses: $", total)
    print("Budget: $", budget)

def update_budget(conn, user_id):
    """Prompt the user to update the budget and save it to the database."""
    budget = float(input('Enter budget: '))
    with conn:
        conn.execute('''
            UPDATE users SET budget = ? WHERE id = ?
        ''', (budget, user_id))
    print("Budget updated successfully!")

def main():
    """Main function to run the expense tracker application."""
    print("Welcome to Simple Expense Tracker!")
    conn = init_db()
    user_id = ''
    while True:
        if not user_id:
            username = input('Please input username ("exit" to exit): ')
            if username.lower() == 'exit':
                break

            user_id = fetch_or_create_user_id(conn, username)
            print("")
            print(f"Welcome, {username}!")
            check_budget(conn, user_id)

        show_menu()
        choice = input('Enter your choice: ')

        if choice == '1':
            add_expense(conn, user_id)
        elif choice == '2':
            view_expense_summary(conn, user_id)
        elif choice == '3':
            export_expenses(conn, user_id)
        elif choice == '4':
            update_budget(conn, user_id)
        elif choice == '5':
            print("Exiting...")
            user_id = ''
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()