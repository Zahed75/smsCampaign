from django.db import models


class DailySalesReport(models.Model):
    customer_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    invoice_no = models.CharField(max_length=50)
    item_code = models.CharField(max_length=50)
    receivable_value = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_eligible(self):
        return self.receivable_value >= 5000


class OutletManager(models.Model):
    showroom_code = models.CharField(max_length=50, unique=True)
    bm_number = models.CharField(max_length=50)

    def __str__(self):
        return self.showroom_code

class CustomerOTP(models.Model):
    mobile_no = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mobile_no


class GiftCard(models.Model):
    product_code = models.CharField(max_length=50)
    gift_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.gift_name


class CustomerGiftSelection(models.Model):
    customer_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    product_code = models.CharField(max_length=50)
    showroom_code = models.CharField(max_length=50)
    gift_card = models.ForeignKey(GiftCard, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name
