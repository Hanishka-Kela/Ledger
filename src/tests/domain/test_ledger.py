from datetime import datetime
from uuid import uuid4

from src.domain.entry import Entry, EntryType
from src.domain.transaction import Transaction
from application.ledger_service import LedgerService


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


def test_ledger_service_balances():
    print("\n--- Testing LedgerService Multi-Transaction Flow ---")
    service = LedgerService()

    alice_wallet = uuid4()
    bob_wallet = uuid4()
    system_pool = uuid4()

    # Transaction 1: Alice deposits 50000 paise (₹500)
    tx1_id = uuid4()
    tx1 = Transaction(
        transaction_id=tx1_id,
        timestamp=datetime.now(),
        description="Initial deposit to Alice",
        entries=[
            Entry(
                entry_id=uuid4(),
                transaction_id=tx1_id,
                account_id=alice_wallet,
                type=EntryType.DEBIT,
                amount=50000,
            ),
            Entry(
                entry_id=uuid4(),
                transaction_id=tx1_id,
                account_id=system_pool,
                type=EntryType.CREDIT,
                amount=50000,
            ),
        ],
    )
    service.post_transaction(tx1)

    # Transaction 2: Alice transfers 20000 paise (₹200) to Bob
    tx2_id = uuid4()
    tx2 = Transaction(
        transaction_id=tx2_id,
        timestamp=datetime.now(),
        description="Alice transfers to Bob",
        entries=[
            Entry(
                entry_id=uuid4(),
                transaction_id=tx2_id,
                account_id=bob_wallet,
                type=EntryType.DEBIT,
                amount=20000,
            ),
            Entry(
                entry_id=uuid4(),
                transaction_id=tx2_id,
                account_id=alice_wallet,
                type=EntryType.CREDIT,
                amount=20000,
            ),
        ],
    )
    service.post_transaction(tx2)

    # Verify Alice's balance: +50000 (debit) - 20000 (credit) = 30000 paise (₹300)
    alice_balance = service.get_account_balance(alice_wallet)
    print(f"Alice's balance: {alice_balance} paise")
    assert alice_balance == 30000

    # Verify Bob's balance: +20000 (debit) = 20000 paise (₹200)
    bob_balance = service.get_account_balance(bob_wallet)
    print(f"Bob's balance: {bob_balance} paise")
    assert bob_balance == 20000

    # Verify System Pool balance: -50000 (credit) = -50000 paise (-₹500)
    system_balance = service.get_account_balance(system_pool)
    print(f"System pool balance: {system_balance} paise")
    assert system_balance == -50000

    print("SUCCESS: LedgerService balance calculations are completely verified!")


if __name__ == "__main__":
    test_ledger()
    test_ledger_service_balances()