from django.urls import path
from .views import *


from .views import (
    GenerateOTPView, VerifyOTPView, GiftSelectionView,
    UploadDailySalesReportView, UploadOutletInformationView
)

urlpatterns = [
    path('api/generate-otp/', GenerateOTPView.as_view(), name='generate-otp'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('api/gifts/', GiftSelectionView.as_view(), name='gift-selection'),
    path('api/upload-sales-report/', UploadDailySalesReportView.as_view(), name='upload-sales-report'),
    path('api/upload-outlet-info/', UploadOutletInformationView.as_view(), name='upload-outlet-info'),
]
