from django.urls import path
from .views import *

urlpatterns = [
    path('generate-otp/', GenerateOTPView.as_view(), name='generate-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('gifts/', GiftSelectionView.as_view(), name='gift-selection'),
    path('upload-sales/', UploadSalesReportView.as_view(), name='upload-sales'),
]
