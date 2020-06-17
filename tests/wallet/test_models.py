from django.db import IntegrityError

import pytest

from wallet.models import Transaction


pytestmark = pytest.mark.django_db


def test_wallet_creation(wallet):
    assert len(wallet.name) == 36
    assert wallet.balance == 0


def test_deposit(wallet):
    wallet.deposit(1)
    assert wallet.balance == 1
    wallet.deposit(2)
    assert wallet.balance == 3


def test_withdraw(wallets):
    wallet1, wallet2 = wallets
    wallet1.deposit(10)
    wallet1.withdraw(6, wallet2)
    assert wallet1.balance == 4
    assert wallet2.balance == 6
    transaction = Transaction.objects.last()
    assert transaction.amount == 6
    assert transaction.wallet_from == wallet1
    assert transaction.wallet_to == wallet2

    wallet2.withdraw(3, wallet1)
    assert wallet1.balance == 7
    assert wallet2.balance == 3


def test_non_negative_balance(wallets):
    wallet1, wallet2 = wallets
    with pytest.raises(IntegrityError):
        wallet1.deposit(-1)

    assert wallet1.balance == 0

    wallet1.deposit(100)
    with pytest.raises(IntegrityError):
        wallet1.withdraw(110, wallet2)

    assert wallet1.balance == 100
    assert wallet2.balance == 0
