from django.db import models


class Campaign(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    channels = models.TextField(help_text="List of participating outlets")

    def __str__(self):
        return self.name

class Customer(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number

class QRCodeScan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.phone_number} - {'Verified' if self.verified else 'Pending'}"

class OTPVerification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.customer.phone_number} - {'Verified' if self.verified else 'Pending'}"

class Gift(models.Model):
    name = models.CharField(max_length=255)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    discount_percentage = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class GiftRedemption(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    sms_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Gift {self.gift.name} for {self.customer.phone_number} - {'Sent' if self.sms_sent else 'Pending'}"

class SMSLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Sent', 'Sent'), ('Failed', 'Failed')])

    def __str__(self):
        return f"SMS to {self.customer.phone_number} - {self.status}"
