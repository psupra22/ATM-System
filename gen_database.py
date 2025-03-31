import sqlite3

def main():
    db_filename = "atm.db"
    create_database(db_filename)
    populate_database(db_filename)
    print("Database populated with sample users and accounts.")


def create_database(db_name: str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_type TEXT NOT NULL CHECK (account_type IN ('Checking', 'Savings', 'Credit')),
            balance REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            card_company TEXT NOT NULL,
            cardholder_name TEXT NOT NULL,
            card_type TEXT NOT NULL,
            card_number TEXT NOT NULL UNIQUE,
            expiration_date TEXT NOT NULL,
            cvc TEXT NOT NULL,
            pin TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()


def add_user(conn, name, email):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    return cursor.lastrowid  # Returns new user_id


def add_account(conn, user_id, account_type, balance):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO accounts (user_id, account_type, balance) VALUES (?, ?, ?)", (user_id, account_type, balance))
    conn.commit()
    return cursor.lastrowid  # Returns new account_id


def add_card(conn, account_id, card_company, cardholder_name, card_type, card_number, cvc, pin):
    cursor = conn.cursor()
    expiration_date = "12/28"  # Example expiration date
    cursor.execute("""
        INSERT INTO cards (account_id, card_company, cardholder_name, card_type, card_number, expiration_date, cvc, pin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (account_id, card_company, cardholder_name, card_type, card_number, expiration_date, cvc, pin))
    conn.commit()


def populate_database(db_name: str):
    conn = sqlite3.connect(db_name)
    
    # Add two users
    user1_id = add_user(conn, "Alice", "alice@email.com")
    user2_id = add_user(conn, "Bob", "bob@email.com")
    
    # Add accounts for Alice
    acc1 = add_account(conn, user1_id, "Checking", 2000.00)
    acc2 = add_account(conn, user1_id, "Savings", 5000.00)
    
    # Add accounts for Bob
    acc3 = add_account(conn, user2_id, "Checking", 1500.00)
    acc4 = add_account(conn, user2_id, "Savings", 3000.00)
    acc5 = add_account(conn, user2_id, "Credit", -500.00)  # Credit account with negative balance
    
    # Add cards for Alice
    add_card(conn, acc1, "Visa", "Alice", "Debit", "3705113944732746", "487", "1234")
    add_card(conn, acc2, "Mastercard", "Alice", "Credit", "3461791776320947", "415", "5678")
    
    # Add cards for Bob
    add_card(conn, acc3, "Visa", "Bob", "Debit", "3448730162325261", "455", "4321")
    add_card(conn, acc4, "Mastercard", "Bob", "Credit", "3737877849662508", "581", "8765")
    add_card(conn, acc5, "American Express", "Bob", "Credit", "3473461515850660", "698", "9876")
    
    conn.close()


if __name__ == "__main__":
    main()
