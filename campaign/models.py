from django.db import models


class DailySalesReport(models.Model):
    customer_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    invoice_no = models.CharField(max_length=50)
    item_code = models.CharField(max_length=50)
    receivable_value = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload_file = models.FileField(upload_to='daily_sales_uploads/', null=True, blank=True)

    def is_eligible(self):
        return self.receivable_value >= 5000

    def save(self, *args, **kwargs):
        # Ensure mobile number is always saved as 11-digit with leading zero
        self.mobile_no = str(self.mobile_no).zfill(11)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer_name


class OutletManager(models.Model):
    showroom_code = models.CharField(max_length=50, unique=True)
    bm_number = models.CharField(max_length=50)

    def __str__(self):
        return self.showroom_code

    def save(self, *args, **kwargs):
        # Ensure mobile number is always saved as 11-digit with leading zero
        self.mobile_no = str(self.bm_number).zfill(11)
        super().save(*args, **kwargs)




class CustomerOTP(models.Model):
    mobile_no = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mobile_no






class DailySalesReportUpload(models.Model):
    upload_file = models.FileField(upload_to='daily_sales_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Uploaded file: {self.upload_file.name}"


class OutletManagerUpload(models.Model):
    upload_file = models.FileField(upload_to='outlet_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Uploaded file: {self.upload_file.name}"


class Customer(models.Model):
    customer_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.customer_name} ({self.mobile_no})"


class DiscountGift(models.Model):
    discount_code = models.CharField(max_length=50, unique=True)
    discount_text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.discount_code}: {self.discount_text}"


class DiscountRedemption(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount = models.ForeignKey(DiscountGift, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.customer_name} redeemed {self.discount.discount_code}"
