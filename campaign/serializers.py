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

class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = ['product_code']

class CustomerGiftSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerGiftSelection
        fields = '__all__'
