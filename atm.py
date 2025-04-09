import sqlite3
import re

class ATM:
    def __init__(self, database_name: str) -> None:
        self._sqlite_connection = sqlite3.connect(database_name)  # Establish connection
        self._cursor = self._sqlite_connection.cursor()  # Create cursor
        self._create_database()  # Set up/make sure the database exists
        self._account_id: str = ""
        self._user_id: str = ""

    def _create_database(self) -> None:
        """Create the users, accounts, and cards tables."""
        # Users table (stores basic user information)
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')

        # Accounts table (stores different balances for each user)
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_type TEXT NOT NULL CHECK (account_type IN ('Checking', 'Savings', 'Credit')),
                balance_cents INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')

        # Cards table (links to accounts, not directly to users)
        self._cursor.execute('''
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
        self._sqlite_connection.commit()
    
    def check_card(self, card_number: str, cvc: str, exp: str, pin: str) -> None:
        """Verify if the entered info matches the stored data."""
        self._account_id = ""
        self._user_id = ""  # Reset before checking
        self._cursor.execute('''
            SELECT cards.account_id, accounts.user_id FROM cards
            INNER JOIN accounts ON cards.account_id = accounts.account_id
            WHERE cards.card_number = ? AND cards.cvc = ? AND cards.expiration_date = ? AND cards.pin = ?
        ''', (card_number, cvc, exp, pin))  # Find id from card information
        result = self._cursor.fetchone()
        if not result:
            raise ValueError("Invalid Card Information, no match found")
        
        self._account_id, self._user_id = result

    def withdraw(self, dollars: str, cents: str) -> None:
        """Withdraws given amount from the cards account"""
        total_cents: int = self._to_cents(dollars, cents)  # Convert to cents
        self._valid_amount(total_cents)  # Make sure given amount is valid
        result: tuple[str, str] = self._balance_cents
        account_type: str = result[0]
        balance: int = int(result[1])
        if account_type != "Credit" and total_cents > balance:  # Only a credit account can have a negative balance
            raise ValueError("Insufficient funds")
        
        self._balance_cents: int = balance - total_cents
        print(f"Withdrawal successful! New balance: {self.balance_string}")

    def deposit(self, dollars: str, cents: str) -> None:
        """Deposits given amount into the cards account"""
        total_cents: int = self._to_cents(dollars, cents)  # Convert to cents
        self._valid_amount(total_cents)  # Make sure given amount is valid
        balance: int = int(self._balance_cents[1])  # Get current card balance
        self._balance_cents: int = balance + total_cents
        print(f"Deposit successful! New balance: {self.balance_string}")

    def transfer(self, dollars: str, cents: str) -> None:
        """Transfers money from the current account to another account under the same user"""
        total_cents: int = self._to_cents(dollars, cents)  # Convert to cents
        self._valid_amount(total_cents)  # Make sure given amount is valid
        choices: list[int] = []
        for account in self._accounts:  # Get all available accounts for the user
            print(f"Account: {account[0]}, Type: {account[1]}")
            choices.append(account[0])

        while True:  # Select destination account
            try:
                choice = int(input("Transfer to which account: ").strip())  # Ensure choice is an integer
                if choice in choices and choice != self._account_id:  # Prevent self-transfer
                    break

                print("Invalid choice. Please select a valid account.")
            except ValueError:
                print("Please enter a valid account number.")

        self.withdraw(dollars, cents)  # Use withdraw to take the money out
        self._cursor.execute('''
            SELECT balance_cents FROM accounts WHERE 
            account_id = ? AND
            user_id = ?
        ''', (choice, self._user_id,))  # Get recipients balance
        result = self._cursor.fetchone()
        if not result:
            raise ValueError("Recipient account not found.")

        recipient_balance: int = result[0]
        new_recipient_balance = recipient_balance + total_cents
        self._cursor.execute('''
            UPDATE accounts SET balance_cents = ? WHERE 
            account_id = ? AND 
            user_id = ?
        ''', (new_recipient_balance, choice, self._user_id))  # Set new balance
        self._sqlite_connection.commit()
        r_dollars: int = new_recipient_balance // 100
        r_cents: int = new_recipient_balance % 100
        print(f"Transfer successful! Recipient account balance: ${r_dollars}.{r_cents:02}")

    def change_pin(self, pin: str) -> None:
        self._cursor.execute('''
            SELECT pin FROM cards WHERE
            account_id = ?
        ''', (self._account_id,))  # Get current pin
        result = self._cursor.fetchone()
        if not result:
            raise ValueError("Account not found")
        
        current_pin: str = result[0]
        if pin != current_pin:  # Make sure entered pin matches current pin
            raise ValueError("Wrong pin")
        
        while True:
            new_pin: str = input("Enter new pin: ").strip()
            confirm_pin: str = input("Confirm pin: ").strip()
            if (new_pin == confirm_pin) and (len(new_pin) == 4):
                break
        
        self._cursor.execute('''
            UPDATE cards SET pin = ? WHERE
            account_id = ?
        ''', (new_pin, self._account_id,))  # Set the new pin
        self._sqlite_connection.commit()
        print("Pin changed successfully")
    
    def close(self) -> None:
        """Close the database connection."""
        self._sqlite_connection.close()

    @staticmethod
    def scan_card() -> list[str]:
        """Get all of the card information and ensure it resembles a card"""
        print("INSERT CARD")
        card_number: str = input("Card Number: ").strip()
        matches = re.search(r"^\d{16}$", card_number)  # 16 digit number
        if not matches:
            raise ValueError("Invalid card number")

        cvc: str = input("CVC: ").strip()
        matches = re.search(r"^\d{3}$", cvc)  # 3 digit number
        if not matches:
            raise ValueError("Invalid CVC")

        exp: str = input("Expiration Date (MM/YY): ").strip()
        matches = re.search(r"^\d{2}/\d{2}$", exp)  # XX/XX form
        if not matches:
            raise ValueError("Invalid expiration date")

        pin: str = input("Enter PIN: ").strip()
        matches = re.search(r"^\d{4}$", pin)  # 4 digit number
        if not matches:
            raise ValueError("Invalid PIN")

        return [card_number, cvc, exp, pin]

    @staticmethod
    def print_menu() -> None:
        print("""
            MENU
            ------------------
            1: WITHDRAW
            2: DEPOSIT
            3: TRANSFER
            4: CHECK BALANCE
            5: CHANGE PIN
            0: EXIT
        """)

    @staticmethod
    def _to_cents(dollars: str, cents: str) -> int:
        if int(dollars) < 0:  # Ensure negative cents if negative dollars
            return (int(dollars) * 100) - int(cents)
        else:
            return (int(dollars) * 100) + int(cents)

    @staticmethod
    def _valid_amount(amount: int) -> None:
        if amount <= 0:  # Can't be 0 or negative
            raise ValueError("Invalid amount")

    @property
    def _balance_cents(self) -> tuple[str, str]:
        self._cursor.execute('''
            SELECT account_type, balance_cents FROM accounts WHERE
            account_id = ? AND
            user_id = ?
        ''', (self._account_id, self._user_id,))  # Find the account type and balance
        result = self._cursor.fetchone()
        if not result:
            raise ValueError("Balance not found")
        
        return result
    
    @_balance_cents.setter
    def _balance_cents(self, new_balance: int) -> None:
        self._cursor.execute('''
            UPDATE accounts SET balance_cents = ? WHERE
            account_id = ? AND 
            user_id = ?
        ''', (new_balance, self._account_id, self._user_id))  # Update the account balance
        self._sqlite_connection.commit()

    @property
    def _accounts(self) -> list[tuple[str, str]]:
        self._cursor.execute('''
            SELECT account_id, account_type FROM accounts WHERE 
            user_id = ?
        ''', (self._user_id,))
    
        result = self._cursor.fetchall()
        if not result:
            return []
        
        return result

    @property
    def balance_string(self) -> str:
        total_cents: int = int(self._balance_cents[1])
        dollars: int = total_cents // 100
        cents: int = total_cents % 100

        return f"${dollars}.{cents:02}"
