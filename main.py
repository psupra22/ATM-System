import re
import sys
import shutil
from atm import ATM

def main() -> None:
    atm: ATM = ATM("atm.db")  # Opens the database
    atm_loop(atm)
    atm.close()


def clear_screen():
    columns = shutil.get_terminal_size().columns
    print("\n" * columns)  # Creates a blank space instead of using system calls


def get_input(atm: ATM) -> int:
    while True:
        atm.print_menu()
        try:
            return int(input("Choose: ").strip())
        except ValueError:
            clear_screen()
            print("Input must be a integer")


def get_amount(prompt: str) -> tuple[str, str]:
    amount: str = input(prompt).strip()
    matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", amount)
    if not matches: 
        raise ValueError("Invalid amount")
    
    return matches.group("dollars"), matches.group("cents")


def atm_loop(atm: ATM) -> None:
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
                    amount: tuple[str, str] = get_amount("Amount to withdraw: ")
                    atm.withdraw(amount[0], amount[1])
                case 2:
                    amount = get_amount("Amount to deposit: ")
                    atm.deposit(amount[0], amount[1])
                case 3:
                    amount = get_amount("Transfer amount: ")
                    atm.transfer(amount[0], amount[1])
                case 4:
                    print(f"Current balance: {atm.balance_string}")
                case 5:
                    atm.change_pin(input("Enter your pin: ").strip())
                case 0:
                    print("Thank you for using our ATM")
                    break
                case _:
                    print("Invalid option")
        except ValueError as message:
            print(message)


if __name__ == "__main__":
    main()
