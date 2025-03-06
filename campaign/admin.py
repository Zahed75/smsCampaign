from django.contrib import admin
from .models import *
import pandas as pd


@admin.register(DailySalesReportUpload)
class DailySalesReportUploadAdmin(admin.ModelAdmin):
    list_display = ('upload_file', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        if obj.upload_file:  # Check if a file is uploaded
            try:
                df = pd.read_excel(obj.upload_file, engine='openpyxl')
                required_columns = {'Customer Name', 'Mobile No', 'Invoice No', 'Item Code', 'Receivable Value'}
                if not required_columns.issubset(df.columns):
                    self.message_user(request, "Invalid file format. Required columns missing.", level='error')
                else:
                    for _, row in df.iterrows():
                        DailySalesReport.objects.create(
                            customer_name=row['Customer Name'],
                            mobile_no=row['Mobile No'],
                            invoice_no=row['Invoice No'],
                            item_code=row['Item Code'],
                            receivable_value=row['Receivable Value']
                        )
                    self.message_user(request, "Daily Sales Report uploaded successfully.")
            except Exception as e:
                self.message_user(request, f"Failed to process file: {str(e)}", level='error')
        super().save_model(request, obj, form, change)


@admin.register(OutletManagerUpload)
class OutletManagerUploadAdmin(admin.ModelAdmin):
    list_display = ('upload_file', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        if obj.upload_file:  # Check if a file is uploaded
            try:
                df = pd.read_excel(obj.upload_file, engine='openpyxl')
                df.columns = df.columns.str.strip().str.lower()
                required_columns = {'suffix', 'bm number'}
                if not required_columns.issubset(set(df.columns)):
                    self.message_user(request, "Invalid file format. Required 'Suffix' and 'BM Number' columns.",
                                      level='error')
                else:
                    for _, row in df.iterrows():
                        OutletManager.objects.update_or_create(
                            showroom_code=row['suffix'],
                            defaults={'bm_number': row['bm number']}
                        )
                    self.message_user(request, "Outlet information uploaded successfully.")
            except Exception as e:
                self.message_user(request, f"Failed to process file: {str(e)}", level='error')
        super().save_model(request, obj, form, change)


@admin.register(OutletManager)
class OutletManagerAdmin(admin.ModelAdmin):
    list_display = ('showroom_code', 'bm_number')
    search_fields = ('showroom_code', 'bm_number')


@admin.register(DailySalesReport)
class DailySalesReportAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'invoice_no', 'item_code', 'receivable_value', 'mobile_no')




@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'mobile_no')
    search_fields = ('customer_name', 'mobile_no')


@admin.register(DiscountGift)
class DiscountGiftAdmin(admin.ModelAdmin):
    list_display = ('discount_code', 'discount_text')
    search_fields = ('discount_code',)


@admin.register(DiscountRedemption)
class DiscountRedemptionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'discount', 'redeemed_at')
    search_fields = ('customer__customer_name', 'discount__discount_code')


admin.site.register(CustomerOTP)

