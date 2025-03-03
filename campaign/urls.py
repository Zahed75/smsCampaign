from django.urls import path
from .views import *

urlpatterns = [
    path('generate-otp/', GenerateOTPView.as_view(), name='generate_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('gift-selection/', GiftSelectionView.as_view(), name='gift_selection'),
]
