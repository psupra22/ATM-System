# ATM System
A simple ATM simulation in Python that allows users to withdraw, deposit, transfer funds, and check their balance. The system validates card details and interacts with an SQLite database.

## Features
- User authentication via card details
- Withdraw and deposit money
- Transfer funds between accounts
- Check account balance
- Change PIN
- Database-backed user and account management

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/psupra22/ATM-System
   cd ATM-System
   ```

2. Generate the database(optional):
    ```sh
    python gen_database.py
    ```
    You must make sure the .db file does not already exist before running this.

## Usage
1. Run the ATM system:
    ```sh
    python main.py
    ```

2. Follow the on-screen instructions to interact with the ATM.

## Testing
To run unit tests, execute:
```sh
pytest test_atm.py
```

## License
This project is licensed under the MIT License.

## Contact
For any inquiries, feel free to reach out at psupra521@gmail.com.
