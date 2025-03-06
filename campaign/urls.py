from django.urls import path
from .views import *

urlpatterns = [


    path('api/upload-daily-sales/', UploadDailySalesReportView.as_view(), name='upload_daily_sales'),
    path('api/upload-outlet-info/', UploadOutletInformationView.as_view(), name='upload_outlet_info'),
    path('api/customer-list-create/', customer_list_create, name='customer_list_create'),
    path('api/verifyOtp/',verify_otp),
    path('api/discount-gift-list/', discount_gift_list_create, name='discount_gift_list'),
    path('api/redeem-discount/', redeem_discount, name='redeem_discount'),
]
