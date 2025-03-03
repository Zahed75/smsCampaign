import random
from campaign.models import *
from Utility.smsHandlers import *


def generate_otp(mobile_no):
    otp = str(random.randint(100000, 999999))
    CustomerOTP.objects.update_or_create(mobile_no=mobile_no, defaults={'otp': otp})

    message = f"Your OTP code is {otp}. It is valid for 10 minutes."
    return send_sms(mobile_no, message)
