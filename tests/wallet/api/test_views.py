import csv
from decimal import Decimal
from io import StringIO

from django.urls import reverse
from django.utils.http import urlencode

import pytest
from freezegun import freeze_time

from wallet.models import Transaction, Wallet


pytestmark = pytest.mark.django_db


def test_create_wallet(client):
    response = client.post(reverse('wallet-list'))
    assert response.status_code == 201
    data = response.json()
    assert data == {
        'name': Wallet.objects.get().name,
        'balance': '0.0000',
    }


def test_transaction_deposit(client, wallet):
    response = client.post(reverse('transaction-deposit', kwargs={'wallet_name': wallet.name}), {'amount': '100.01'})
    assert response.status_code == 201
    transaction = Transaction.objects.get()
    assert transaction.amount == Decimal('100.01')
    assert transaction.wallet_to == wallet
    assert transaction.wallet_from is None


def test_transaction_deposit_wrong_amount(client, wallet):
    response = client.post(reverse('transaction-deposit', kwargs={'wallet_name': wallet.name}), {'amount': '-10'})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Wrong amount'}


def test_transaction_withdrawal(client, wallets):
    wallet1, wallet2 = wallets
    wallet1.deposit(100)
    response = client.post(
        reverse('transaction-withdrawal', kwargs={'wallet_name': wallet1.name}),
        {'amount': '12.34', 'wallet_to': wallet2.name,},
    )
    assert response.status_code == 201
    transaction = Transaction.objects.last()
    assert transaction.amount == Decimal('12.34')
    assert transaction.wallet_to == wallet2
    assert transaction.wallet_from == wallet1


def test_transaction_withdraw_wrong_amount(client, wallets):
    wallet1, wallet2 = wallets
    response = client.post(
        reverse('transaction-withdrawal', kwargs={'wallet_name': wallet1.name}),
        {'amount': '12.34', 'wallet_to': wallet2.name,},
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Wrong amount'}


def test_transactions_wrong_wallet(client):
    response = client.get(reverse('transaction-list', kwargs={'wallet_name': '123'}))
    assert response.status_code == 404
    assert response.json() == {'detail': 'Wallet not found'}


def test_transactions_list(client, wallets_with_transactions):
    wallet1, wallet2 = wallets_with_transactions
    response = client.get(reverse('transaction-list', kwargs={'wallet_name': wallet1.name}))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert Decimal(data[0]['amount']) == 100
    assert data[0]['wallet_to'] == wallet1.name
    assert Decimal(data[1]['amount']) == 50
    assert data[1]['wallet_to'] == wallet2.name
    assert data[1]['wallet_from'] == wallet1.name

    wallet2.withdraw(25, wallet1)
    response = client.get(reverse('transaction-list', kwargs={'wallet_name': wallet1.name}))
    data = response.json()
    assert len(data) == 3
    assert Decimal(data[2]['amount']) == 25
    assert data[2]['wallet_to'] == wallet1.name
    assert data[2]['wallet_from'] == wallet2.name


def test_transactions_list_filters(client, wallets):
    wallet1, wallet2 = wallets
    with freeze_time('2020-01-01'):
        wallet1.deposit(100)
        wallet1.withdraw(20, wallet2)

    with freeze_time('2020-01-02'):
        wallet2.withdraw(10, wallet1)

    t1 = {'created': '2020-01-01 00:00:00', 'amount': '100.0000', 'wallet_to': wallet1.name}
    t2 = {'created': '2020-01-01 00:00:00', 'amount': '20.0000', 'wallet_to': wallet2.name, 'wallet_from': wallet1.name}
    t3 = {'created': '2020-01-02 00:00:00', 'amount': '10.0000', 'wallet_to': wallet1.name, 'wallet_from': wallet2.name}

    url = reverse('transaction-list', kwargs={'wallet_name': wallet1.name})

    test_params = (
        ({'type': 'deposit'}, [t1]),
        ({'type': 'income'}, [t1, t3]),
        ({'type': 'withdrawal'}, [t2]),
        ({}, [t1, t2, t3]),
        ({'date_from': '2020-01-02 00:00:00'}, [t3]),
        ({'type': 'income', 'date_to': '2020-01-02 00:00:00'}, [t1]),
        ({'date_from': '123q'}, {'detail': 'Wrong date format'}),
    )

    for params, expected in test_params:
        data = client.get(f'{url}?{urlencode(params)}').json()
        assert data == expected


def test_csv_export(client, wallets_with_transactions):
    wallet1, _ = wallets_with_transactions
    response = client.get(reverse('transaction-export', kwargs={'wallet_name': wallet1.name}))
    reader = csv.reader(StringIO(response.content.decode()))
    assert next(reader) == ['created', 'from', 'to', 'amount']
    _, _, wallet_to, amount = next(reader)
    assert wallet_to == wallet1.name
    assert Decimal(amount) == 100
