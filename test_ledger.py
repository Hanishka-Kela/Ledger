from datetime import datetime
from uuid import uuid4

from src.domain.entry import Entry, EntryType
from src.domain.transacations import Transaction


def test_ledger():
    # Setup test IDs
    transaction_id = uuid4()
    account_a = uuid4()
    account_b = uuid4()

    # 1. Test a valid balanced transaction (Debit 10000 paise = Credit 10000 paise)
    valid_entry_1 = Entry(
        entry_id=uuid4(),
        transaction_id=transaction_id,
        account_id=account_a,
        type=EntryType.DEBIT,
        amount=10000,
    )
    valid_entry_2 = Entry(
        entry_id=uuid4(),
        transaction_id=transaction_id,
        account_id=account_b,
        type=EntryType.CREDIT,
        amount=10000,
    )

    valid_transaction = Transaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(),
        description="Valid Transfer",
        entries=[valid_entry_1, valid_entry_2],
    )

    print("Testing Balanced Transaction...")
    assert valid_transaction.is_valid() is True
    print("SUCCESS: Balanced transaction passed!")

    # 2. Test an unbalanced transaction (Debit 10000 vs Credit 9000)
    unbalanced_entry_2 = Entry(
        entry_id=uuid4(),
        transaction_id=transaction_id,
        account_id=account_b,
        type=EntryType.CREDIT,
        amount=9000,
    )

    unbalanced_transaction = Transaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(),
        description="Unbalanced Transfer",
        entries=[valid_entry_1, unbalanced_entry_2],
    )

    print("\nTesting Unbalanced Transaction...")
    assert unbalanced_transaction.is_valid() is False
    print("SUCCESS: Unbalanced transaction correctly returned False!")

    # 3. Test a transaction with fewer than 2 entries
    incomplete_transaction = Transaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(),
        description="Incomplete Transfer",
        entries=[valid_entry_1],
    )

    print("\nTesting Incomplete Transaction (< 2 entries)...")
    try:
        incomplete_transaction.is_valid()
        print("FAIL: Expected ValueError was not raised!")
    except ValueError as e:
        print(f"SUCCESS: Caught expected error -> '{e}'")


if __name__ == "__main__":
    test_ledger()