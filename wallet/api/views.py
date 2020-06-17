import csv
from datetime import datetime

from django.db import IntegrityError
from django.http import HttpResponse
from django.utils.functional import cached_property

from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from wallet.api.exceptions import WrongAmountError, WrongDateFormatError
from wallet.api.serializers import (
    BaseTransactionSerializer,
    DepositTransactionSerializer,
    WalletSerializer,
    WithdrawalTransactionSerializer,
)
from wallet.models import Transaction, Wallet


class WalletViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class TransactionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Transaction.objects.all()
    serializer_class = BaseTransactionSerializer

    @cached_property
    def wallet(self):
        wallet_name = self.kwargs.get('wallet_name')
        try:
            return Wallet.objects.get(name=wallet_name)
        except Wallet.DoesNotExist:
            raise exceptions.NotFound('Wallet not found')

    def get_queryset(self):
        transaction_type = self.request.query_params.get('type')
        if transaction_type == 'income':
            qs = self.wallet.incomes
        elif transaction_type == 'deposit':
            qs = self.wallet.incomes.filter(wallet_from__isnull=True)
        elif transaction_type == 'withdrawal':
            qs = self.wallet.payments
        else:
            qs = self.wallet.transactions

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise WrongDateFormatError
            qs = qs.filter(created__gte=date_from)

        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise WrongDateFormatError
            qs = qs.filter(created__lt=date_to)

        return qs

    @action(methods=['get'], detail=False)
    def export(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(['created', 'from', 'to', 'amount'])
        for item in serializer.data:
            writer.writerow([item['created'], item.get('wallet_from', ''), item['wallet_to'], item['amount']])
        return response

    @action(methods=['post'], detail=False)
    def deposit(self, request, **kwargs):
        serializer = DepositTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.wallet.deposit(serializer.validated_data['amount'])
        except IntegrityError:
            raise WrongAmountError
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def withdrawal(self, request, **kwargs):
        serializer = WithdrawalTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            wallet_to = Wallet.objects.get(name=serializer.validated_data['wallet_to'])
        except Wallet.DoesNotExist:
            raise exceptions.NotFound('Wallet not found')

        try:
            self.wallet.withdraw(serializer.validated_data['amount'], wallet_to)
        except IntegrityError:
            raise WrongAmountError

        return Response(status=status.HTTP_201_CREATED)
