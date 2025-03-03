# import requests
# from django.conf import settings  # Import settings to fetch the API key
#
# def send_sms(phone_number, message):
#     api_key = settings.SMS_API_KEY  # Retrieve the API key from settings
#     url = "https://sysadmin.muthobarta.com/api/v1/send-sms"
#     headers = {
#         "Authorization": f"Token {api_key}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "receiver": phone_number,
#         "message": message,
#         "remove_duplicate": True
#     }
#     response = requests.post(url, json=data, headers=headers)
#     return response.json()


import random
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomerOTP, CustomerGiftSelection, GiftCard, DailySalesReport
from .serializers import CustomerOTPSerializer, GiftCardSerializer, CustomerGiftSelectionSerializer
from utilities.smsHandler import send_sms  # Import SMS handler

class GenerateOTPView(APIView):
    def post(self, request):
        mobile_no = request.data.get('mobile_no')
        otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
        CustomerOTP.objects.update_or_create(mobile_no=mobile_no, defaults={'otp': otp})

        # Send OTP via SMS Gateway
        message = f"Your OTP code is {otp}. It is valid for 10 minutes."
        response = send_sms(mobile_no, message)

        if response.get("status") == "success":
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    def post(self, request):
        mobile_no = request.data.get('mobile_no')
        entered_otp = request.data.get('otp')

        try:
            otp_record = CustomerOTP.objects.get(mobile_no=mobile_no)
            if otp_record.otp == entered_otp:
                otp_record.delete()  # Remove OTP after successful verification
                return Response({"message": "OTP verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomerOTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND)
