import pytest

from wallet.models import Wallet


@pytest.fixture
def wallet_factory():
    def f():
        return Wallet.objects.create()

    return f


@pytest.fixture
def wallet(wallet_factory):
    return wallet_factory()


@pytest.fixture
def wallets(wallet_factory):
    wallet1 = wallet_factory()
    wallet2 = wallet_factory()
    return wallet1, wallet2


@pytest.fixture
def wallets_with_transactions(wallets):
    wallet1, wallet2 = wallets
    wallet1.deposit(100)
    wallet1.withdraw(50, wallet2)
    return wallet1, wallet2
