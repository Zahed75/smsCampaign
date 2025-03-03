from django.urls import path
from .views import *


from .views import (
    GenerateOTPView, VerifyOTPView, GiftSelectionView,
    UploadDailySalesReportView, UploadOutletInformationView
)

urlpatterns = [
    path('generate-otp/', GenerateOTPView.as_view(), name='generate-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('gifts/', GiftSelectionView.as_view(), name='gift-selection'),
    path('upload-sales-report/', UploadDailySalesReportView.as_view(), name='upload-sales-report'),
    path('upload-outlet-info/', UploadOutletInformationView.as_view(), name='upload-outlet-info'),
]
