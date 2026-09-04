from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.application.ledger_service import (
    JournalEntryInput,
    LedgerService
)

from src.domain.account import (
    Account,
    AccountType
)

from src.domain.entry import (
    Entry,
    EntryType
)


@pytest.fixture
def repositories():
    account_repository = MagicMock()
    transaction_repository = MagicMock()
    entry_repository = MagicMock()

    return (
        account_repository,
        transaction_repository,
        entry_repository
    )


@pytest.fixture
def ledger_service(repositories):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    return LedgerService(
        account_repository=account_repository,
        transaction_repository=transaction_repository,
        entry_repository=entry_repository
    )


def test_post_transaction_successfully_posts_asset_transfer(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    source_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    destination_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Bank",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.side_effect = [
        source_account,
        destination_account
    ]

    entry_repository.get_by_account_id.return_value = [
        Entry(
            entry_id=uuid4(),
            transaction_id=uuid4(),
            account_id=source_account.account_id,
            type=EntryType.DEBIT,
            amount=1000
        )
    ]

    transaction = ledger_service.post_transaction(
        requester_user_id=owner_id,
        source_account_id=source_account.account_id,
        destination_account_id=destination_account.account_id,
        amount=300,
        description="Move cash to bank"
    )

    assert transaction.description == "Move cash to bank"
    assert len(transaction.entries) == 2
    assert transaction.is_valid() is True

    source_entry = transaction.entries[0]
    destination_entry = transaction.entries[1]

    assert source_entry.account_id == source_account.account_id
    assert source_entry.type == EntryType.CREDIT
    assert source_entry.amount == 300

    assert destination_entry.account_id == destination_account.account_id
    assert destination_entry.type == EntryType.DEBIT
    assert destination_entry.amount == 300

    assert source_entry.transaction_id == transaction.transaction_id
    assert destination_entry.transaction_id == transaction.transaction_id

    transaction_repository.create.assert_called_once_with(
        transaction
    )

    assert entry_repository.create.call_count == 2


def test_post_transaction_rejects_missing_source_account(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    account_repository.get_by_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Source account does not exist"
    ):
        ledger_service.post_transaction(
            requester_user_id=uuid4(),
            source_account_id=uuid4(),
            destination_account_id=uuid4(),
            amount=100,
            description="Transfer"
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_transaction_rejects_unauthorized_source_account(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    source_account = Account(
        account_id=uuid4(),
        owner_id=uuid4(),
        name="Cash",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.return_value = source_account

    with pytest.raises(
        ValueError,
        match="Not authorized to use source account"
    ):
        ledger_service.post_transaction(
            requester_user_id=uuid4(),
            source_account_id=source_account.account_id,
            destination_account_id=uuid4(),
            amount=100,
            description="Transfer"
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_transaction_rejects_missing_destination_account(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    source_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.side_effect = [
        source_account,
        None
    ]

    with pytest.raises(
        ValueError,
        match="Destination account does not exist"
    ):
        ledger_service.post_transaction(
            requester_user_id=owner_id,
            source_account_id=source_account.account_id,
            destination_account_id=uuid4(),
            amount=100,
            description="Transfer"
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -100
    ]
)
def test_post_transaction_rejects_non_positive_amount(
    ledger_service,
    repositories,
    amount
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    source_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    destination_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Bank",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.side_effect = [
        source_account,
        destination_account
    ]

    with pytest.raises(
        ValueError,
        match="Amount must be positive"
    ):
        ledger_service.post_transaction(
            requester_user_id=owner_id,
            source_account_id=source_account.account_id,
            destination_account_id=destination_account.account_id,
            amount=amount,
            description="Transfer"
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_transaction_rejects_insufficient_funds(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    source_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    destination_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Bank",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.side_effect = [
        source_account,
        destination_account
    ]

    entry_repository.get_by_account_id.return_value = [
        Entry(
            entry_id=uuid4(),
            transaction_id=uuid4(),
            account_id=source_account.account_id,
            type=EntryType.DEBIT,
            amount=100
        )
    ]

    with pytest.raises(
        ValueError,
        match="Insufficient funds"
    ):
        ledger_service.post_transaction(
            requester_user_id=owner_id,
            source_account_id=source_account.account_id,
            destination_account_id=destination_account.account_id,
            amount=200,
            description="Transfer"
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_transaction_rejects_unbalanced_account_type_combination(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    source_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    destination_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Loan",
        type=AccountType.LIABILITY
    )

    account_repository.get_by_id.side_effect = [
        source_account,
        destination_account
    ]

    entry_repository.get_by_account_id.return_value = [
        Entry(
            entry_id=uuid4(),
            transaction_id=uuid4(),
            account_id=source_account.account_id,
            type=EntryType.DEBIT,
            amount=1000
        )
    ]

    with pytest.raises(
        ValueError,
        match="Transaction would not produce one debit and one credit"
    ):
        ledger_service.post_transaction(
            requester_user_id=owner_id,
            source_account_id=source_account.account_id,
            destination_account_id=destination_account.account_id,
            amount=100,
            description="Invalid transfer"
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_calculate_balance_for_asset_account(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    account = Account(
        account_id=uuid4(),
        owner_id=uuid4(),
        name="Cash",
        type=AccountType.ASSET
    )

    entry_repository.get_by_account_id.return_value = [
        Entry(
            entry_id=uuid4(),
            transaction_id=uuid4(),
            account_id=account.account_id,
            type=EntryType.DEBIT,
            amount=1000
        ),
        Entry(
            entry_id=uuid4(),
            transaction_id=uuid4(),
            account_id=account.account_id,
            type=EntryType.CREDIT,
            amount=300
        )
    ]

    balance = ledger_service._calculate_balance(
        account
    )

    assert balance == 700


def test_calculate_balance_for_liability_account(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    account = Account(
        account_id=uuid4(),
        owner_id=uuid4(),
        name="Loan",
        type=AccountType.LIABILITY
    )

    entry_repository.get_by_account_id.return_value = [
        Entry(
            entry_id=uuid4(),
            transaction_id=uuid4(),
            account_id=account.account_id,
            type=EntryType.CREDIT,
            amount=1000
        ),
        Entry(
            entry_id=uuid4(),
            transaction_id=uuid4(),
            account_id=account.account_id,
            type=EntryType.DEBIT,
            amount=250
        )
    ]

    balance = ledger_service._calculate_balance(
        account
    )

    assert balance == 750


def test_post_journal_owner_funding(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    cash_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    equity_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Owner Equity",
        type=AccountType.EQUITY
    )

    account_repository.get_by_id.side_effect = [
        cash_account,
        equity_account
    ]

    transaction = ledger_service.post_journal(
        requester_user_id=owner_id,
        description="Owner capital",
        entries=[
            JournalEntryInput(
                account_id=cash_account.account_id,
                type=EntryType.DEBIT,
                amount=1000
            ),
            JournalEntryInput(
                account_id=equity_account.account_id,
                type=EntryType.CREDIT,
                amount=1000
            )
        ]
    )

    assert transaction.is_valid() is True
    assert len(transaction.entries) == 2

    assert transaction.entries[0].type == EntryType.DEBIT
    assert transaction.entries[1].type == EntryType.CREDIT

    assert transaction.entries[0].amount == 1000
    assert transaction.entries[1].amount == 1000

    transaction_repository.create.assert_called_once_with(
        transaction
    )

    assert entry_repository.create.call_count == 2


def test_post_journal_supports_liability_transaction(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    cash_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    loan_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Loan Payable",
        type=AccountType.LIABILITY
    )

    account_repository.get_by_id.side_effect = [
        cash_account,
        loan_account
    ]

    transaction = ledger_service.post_journal(
        requester_user_id=owner_id,
        description="Loan received",
        entries=[
            JournalEntryInput(
                account_id=cash_account.account_id,
                type=EntryType.DEBIT,
                amount=5000
            ),
            JournalEntryInput(
                account_id=loan_account.account_id,
                type=EntryType.CREDIT,
                amount=5000
            )
        ]
    )

    assert transaction.is_valid() is True


def test_post_journal_supports_revenue_transaction(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    cash_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    revenue_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Sales Revenue",
        type=AccountType.REVENUE
    )

    account_repository.get_by_id.side_effect = [
        cash_account,
        revenue_account
    ]

    transaction = ledger_service.post_journal(
        requester_user_id=owner_id,
        description="Sale",
        entries=[
            JournalEntryInput(
                account_id=cash_account.account_id,
                type=EntryType.DEBIT,
                amount=500
            ),
            JournalEntryInput(
                account_id=revenue_account.account_id,
                type=EntryType.CREDIT,
                amount=500
            )
        ]
    )

    assert transaction.is_valid() is True


def test_post_journal_supports_expense_transaction(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    expense_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Rent Expense",
        type=AccountType.EXPENSE
    )

    cash_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.side_effect = [
        expense_account,
        cash_account
    ]

    transaction = ledger_service.post_journal(
        requester_user_id=owner_id,
        description="Rent paid",
        entries=[
            JournalEntryInput(
                account_id=expense_account.account_id,
                type=EntryType.DEBIT,
                amount=200
            ),
            JournalEntryInput(
                account_id=cash_account.account_id,
                type=EntryType.CREDIT,
                amount=200
            )
        ]
    )

    assert transaction.is_valid() is True


def test_post_journal_rejects_less_than_two_entries(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    with pytest.raises(
        ValueError,
        match="Journal transaction must contain at least two entries"
    ):
        ledger_service.post_journal(
            requester_user_id=uuid4(),
            description="Invalid",
            entries=[
                JournalEntryInput(
                    account_id=uuid4(),
                    type=EntryType.DEBIT,
                    amount=100
                )
            ]
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_journal_rejects_missing_account(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    account_repository.get_by_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Journal entry account does not exist"
    ):
        ledger_service.post_journal(
            requester_user_id=uuid4(),
            description="Invalid",
            entries=[
                JournalEntryInput(
                    account_id=uuid4(),
                    type=EntryType.DEBIT,
                    amount=100
                ),
                JournalEntryInput(
                    account_id=uuid4(),
                    type=EntryType.CREDIT,
                    amount=100
                )
            ]
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_journal_rejects_unauthorized_account(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    account = Account(
        account_id=uuid4(),
        owner_id=uuid4(),
        name="Cash",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.return_value = account

    with pytest.raises(
        ValueError,
        match="Not authorized to use journal entry account"
    ):
        ledger_service.post_journal(
            requester_user_id=uuid4(),
            description="Invalid",
            entries=[
                JournalEntryInput(
                    account_id=account.account_id,
                    type=EntryType.DEBIT,
                    amount=100
                ),
                JournalEntryInput(
                    account_id=uuid4(),
                    type=EntryType.CREDIT,
                    amount=100
                )
            ]
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_journal_rejects_non_positive_amount(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    account_repository.get_by_id.return_value = account

    with pytest.raises(
        ValueError,
        match="Journal entry amount must be positive"
    ):
        ledger_service.post_journal(
            requester_user_id=owner_id,
            description="Invalid",
            entries=[
                JournalEntryInput(
                    account_id=account.account_id,
                    type=EntryType.DEBIT,
                    amount=0
                ),
                JournalEntryInput(
                    account_id=account.account_id,
                    type=EntryType.CREDIT,
                    amount=0
                )
            ]
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()


def test_post_journal_rejects_unbalanced_transaction(
    ledger_service,
    repositories
):
    (
        account_repository,
        transaction_repository,
        entry_repository
    ) = repositories

    owner_id = uuid4()

    asset_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Cash",
        type=AccountType.ASSET
    )

    equity_account = Account(
        account_id=uuid4(),
        owner_id=owner_id,
        name="Equity",
        type=AccountType.EQUITY
    )

    account_repository.get_by_id.side_effect = [
        asset_account,
        equity_account
    ]

    with pytest.raises(
        ValueError,
        match="Journal transaction is not balanced"
    ):
        ledger_service.post_journal(
            requester_user_id=owner_id,
            description="Invalid journal",
            entries=[
                JournalEntryInput(
                    account_id=asset_account.account_id,
                    type=EntryType.DEBIT,
                    amount=1000
                ),
                JournalEntryInput(
                    account_id=equity_account.account_id,
                    type=EntryType.CREDIT,
                    amount=500
                )
            ]
        )

    transaction_repository.create.assert_not_called()
    entry_repository.create.assert_not_called()