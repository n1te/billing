import uuid

from django.db import models
from django.db.models import Q, CheckConstraint, F
from django.db.transaction import atomic
from django.utils.functional import cached_property
from model_utils.fields import AutoCreatedField


def get_default_name():
    return str(uuid.uuid4())


class Wallet(models.Model):
    name = models.CharField(max_length=36, default=get_default_name)
    balance = models.DecimalField(decimal_places=4, max_digits=12, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='name_idx'),
        ]
        constraints = [
            CheckConstraint(
                check=Q(balance__gte=0),
                name='non_negative_balance')
        ]

    @cached_property
    def transactions(self):
        return Transaction.objects.filter(Q(wallet_from=self) | Q(wallet_to=self))

    @atomic
    def deposit(self, amount):
        self.incomes.create(amount=amount)
        Wallet.objects.filter(pk=self.pk).update(balance=F('balance') + amount)
        self.refresh_from_db()

    @atomic
    def withdraw(self, amount, to):
        self.payments.create(amount=amount, wallet_to=to)
        Wallet.objects.filter(pk=self.pk).update(balance=F('balance') - amount)
        Wallet.objects.filter(pk=to.pk).update(balance=F('balance') + amount)
        self.refresh_from_db()
        to.refresh_from_db()


class Transaction(models.Model):
    created = AutoCreatedField()
    amount = models.DecimalField(decimal_places=4, max_digits=12)
    wallet_from = models.ForeignKey(Wallet, related_name='payments', on_delete=models.CASCADE, null=True)
    wallet_to = models.ForeignKey(Wallet, related_name='incomes', on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['wallet_from'], name='wallet_from_idx'),
            models.Index(fields=['wallet_to'], name='wallet_to_idx'),
        ]
