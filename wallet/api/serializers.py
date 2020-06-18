from rest_framework import serializers

from wallet.api.exceptions import WrongAmountError
from wallet.models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(read_only=True, decimal_places=4, max_digits=12)

    class Meta:
        model = Wallet
        fields = ['name', 'balance']

    def create(self, validated_data):
        return Wallet.objects.create()


class BaseTransactionSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    amount = serializers.DecimalField(decimal_places=4, max_digits=12, read_only=True)
    wallet_to = serializers.CharField(max_length=36, min_length=36, read_only=True, source='wallet_to.name')
    wallet_from = serializers.CharField(max_length=36, min_length=36, read_only=True, source='wallet_from.name')

    class Meta:
        model = Transaction
        fields = ['created', 'amount', 'wallet_from', 'wallet_to']


class DepositTransactionSerializer(BaseTransactionSerializer):
    amount = serializers.DecimalField(decimal_places=4, max_digits=12)


class WithdrawalTransactionSerializer(DepositTransactionSerializer):
    wallet_to = serializers.CharField(max_length=36, min_length=36)

    def validate_amount(self, value):
        if value < 0:
            raise WrongAmountError
        return value
