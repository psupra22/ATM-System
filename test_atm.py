import pytest
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
    assert atm.balance == 2000.00
    atm.check_card("3461791776320947", "415", "12/28", "5678")
    assert atm.balance == 5000.00


def test_withdraw() -> None:
    atm: ATM = ATM("atm.db")
    atm.check_card("3705113944732746", "487", "12/28", "1234")
    atm.withdraw(1000.00)
    assert atm.balance == 1000.00
    with pytest.raises(ValueError):
        atm.withdraw(-5.00)
    with pytest.raises(ValueError):
        atm.withdraw(0.00)
    with pytest.raises(ValueError):
        atm.withdraw(6000.00)


def test_deposit() -> None:
    atm: ATM = ATM("atm.db")
    atm.check_card("3705113944732746", "487", "12/28", "1234")
    atm.deposit(1000.00)
    assert atm.balance == 2000.00
    with pytest.raises(ValueError):
        atm.deposit(-5.00)
    with pytest.raises(ValueError):
        atm.deposit(0.00)
