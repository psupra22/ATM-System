import sys
import shutil
from atm import ATM

def main() -> None:
    atm: ATM = ATM("atm.db")  # Opens the database

    while True:
        try:
            clear_screen()
            card_number, cvc, exp, pin = atm.scan_card()  # Basically like insert card prompt
            atm.check_card(card_number, cvc, exp, pin)  # Checks if card exists in the database
            break
        except ValueError as message:
            print(message)
            try_again: str = input("Do you wish to insert card again(y/n): ").lower().strip()
            if try_again.startswith('y'):
                continue
            atm.close()
            sys.exit(1)

    clear_screen()
    while True:
        choice: int = get_input(atm)
        clear_screen()
        try:
            match choice:
                case 1:
                    amount: float = round(float(input("Amount to withdraw: ").strip()), 2) 
                    atm.withdraw(amount)
                case 2:
                    amount = round(float(input("Amount to deposit: ").strip()), 2) 
                    atm.deposit(amount)
                case 3:
                    atm.transfer(round(float(input("Transfer amount: ").strip()), 2))
                case 4:
                    print(f"Current balance: ${atm.balance:.2f}")
                case 5:
                    atm.change_pin(input("Enter your pin: ").strip())
                case 0:
                    print("Thank you for using our ATM")
                    break
                case _:
                    print("Invalid option")
        except ValueError as message:
            print(message)

    atm.close()


def clear_screen():
    columns = shutil.get_terminal_size().columns
    print("\n" * columns)  # Creates a blank space instead of using system calls


def get_input(atm: ATM) -> int:
    while True:
        atm.print_menu()
        try:
            return int(input("Choose: "))
        except ValueError:
            clear_screen()
            print("Input must be a integer")


if __name__ == "__main__":
    main()
