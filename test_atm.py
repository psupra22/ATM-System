import pytest
import re
from unittest.mock import patch
from atm import ATM

def test_init() -> None:
    atm: ATM = ATM("atm.db")
    assert atm._account_id == ""
    assert atm._user_id == ""


@pytest.mark.parametrize("inputs", [
    (["invalid_card", "123", "12/28", "1234"]),  # Invalid card number
    (["1234567812345678", "12", "12/28", "1234"]),  # Invalid CVC
    (["1234567812345678", "123", "1228", "1234"]),  # Invalid expiration format
    (["1234567812345678", "123", "12/28", "12"]),  # Invalid PIN
])
def test_scan_card_invalid(inputs) -> None:
    with patch("builtins.input", side_effect=inputs):
        with pytest.raises(ValueError):
            ATM.scan_card()


def test_check_card() -> None:
    atm: ATM = ATM("atm.db")
    with pytest.raises(ValueError):
        atm.check_card("1234567891234567", "123", "12/12", "1111")


def test_balance() -> None:
    atm: ATM = ATM("atm.db")
    atm.check_card("3705113944732746", "487", "12/28", "1234")
    assert atm.balance_string == "$2000.00"
    atm.check_card("3461791776320947", "415", "12/28", "5678")
    assert atm.balance_string == "$5000.00"


def test_withdraw() -> None:
    atm: ATM = ATM("atm.db")
    atm.check_card("3705113944732746", "487", "12/28", "1234")
    matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", "1000.00")
    atm.withdraw(matches.group("dollars"), matches.group("cents"))
    assert atm.balance_string == "$1000.00"
    with pytest.raises(ValueError):
        matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", "-5.00")
        atm.withdraw(matches.group("dollars"), matches.group("cents"))
    with pytest.raises(ValueError):
        matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", "0.00")
        atm.withdraw(matches.group("dollars"), matches.group("cents"))
    with pytest.raises(ValueError):
        matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", "6000.00")
        atm.withdraw(matches.group("dollars"), matches.group("cents"))


def test_deposit() -> None:
    atm: ATM = ATM("atm.db")
    atm.check_card("3705113944732746", "487", "12/28", "1234")
    matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", "1000.00")
    atm.deposit(matches.group("dollars"), matches.group("cents"))
    assert atm.balance_string == "$2000.00"
    with pytest.raises(ValueError):
        matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", "-5.00")
        atm.deposit(matches.group("dollars"), matches.group("cents"))
    with pytest.raises(ValueError):
        matches = re.search(r"^(?P<dollars>-?\d+)\.(?P<cents>\d{2})$", "0.00")
        atm.deposit(matches.group("dollars"), matches.group("cents"))
