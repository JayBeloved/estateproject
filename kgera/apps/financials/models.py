from django.db import models
from ..residents.models import Residents
from ..structure.models import HouseType
import datetime

VERIFIED = 1
UNVERIFIED = 0

PAY_STATUS = (
    (VERIFIED, 'Payment Verified'),
    (UNVERIFIED, 'Verification Pending')
)


class ChargesDefinition(models.Model):
    housetype = models.ForeignKey(HouseType, on_delete=models.CASCADE, to_field='htype')
    service_charge = models.DecimalField(max_digits=10, decimal_places=2)
    transformer_levy = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Charges Payable for {self.housetype} for the Year\n" \
               f"Service Charge:N {self.service_charge} | Transformer Levy:N {self.transformer_levy}"


class ResidentFinancialStanding(models.Model):
    resident = models.ForeignKey(Residents, on_delete=models.DO_NOTHING, to_field='resident_code')
    service_charge_outstanding = models.DecimalField(max_digits=10, decimal_places=2)
    transformer_levy_outstanding = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Outs. Service Charge:N {self.service_charge_outstanding} | " \
               f"Outs. Transformer Levy:N {self.transformer_levy_outstanding} "


class ServiceChargePayments(models.Model):
    resident = models.ForeignKey(Residents, on_delete=models.DO_NOTHING, to_field='resident_code')
    payment_date = models.DateField('pay_date', default=datetime.date, null=True)
    payment_note = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveSmallIntegerField('payment_status', choices=PAY_STATUS, default=UNVERIFIED)
    payment_ref = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment Reference - {self.payment_ref} | Amount:N {self.amount}"


class TransformerLevyPayments(models.Model):
    resident = models.ForeignKey(Residents, on_delete=models.DO_NOTHING, to_field='resident_code')
    payment_date = models.DateField('pay_date', default=datetime.date, null=True)
    payment_note = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveSmallIntegerField('payment_status', choices=PAY_STATUS, default=UNVERIFIED)
    payment_ref = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment Reference - {self.payment_ref} | Amount:N {self.amount}"
