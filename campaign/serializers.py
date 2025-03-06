from rest_framework import serializers
from .models import *

class DailySalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySalesReport
        fields = '__all__'

class OutletManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutletManager
        fields = '__all__'

class CustomerOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOTP
        fields = '__all__'







class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_name', 'mobile_no']
        extra_kwargs = {
            'customer_name': {'required': False},  # Make customer_name optional
        }

class DiscountGiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountGift
        fields = '__all__'

class DiscountRedemptionSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    discount = DiscountGiftSerializer()

    class Meta:
        model = DiscountRedemption
        fields = '__all__'
