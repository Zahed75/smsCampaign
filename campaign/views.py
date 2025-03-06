import json

from django.http.response import JsonResponse

from .modules import *


def generate_otp(mobile_no):
    """ Generate a 6-digit OTP, store it, and send via SMS """
    otp = str(random.randint(100000, 999999))

    # Store OTP in database
    CustomerOTP.objects.update_or_create(mobile_no=mobile_no, defaults={'otp': otp})

    # Send OTP via SMS
    message = f"Your OTP code is {otp}. Do not share it with anyone."
    response = send_sms(mobile_no, message)

    if response.get("status") != "success":  # Adjust this based on the API response structure
        print(f"Failed to send OTP: {response}")  # Debugging info

    return otp


class UploadDailySalesReportView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith('.xlsx'):
            return Response({"error": "Only .xlsx files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read Excel file and ensure Mobile No column is treated as a string
            df = pd.read_excel(file, engine='openpyxl', dtype={'Mobile No': str})

            # Convert all Mobile No values to string and ensure they have 11 digits
            df['Mobile No'] = df['Mobile No'].astype(str).str.strip()
            df['Mobile No'] = df['Mobile No'].apply(lambda x: x.zfill(11) if x.isdigit() else x)

            print("🔍 DEBUG: Data read from Excel:")
            print(df.head())  # Print first few rows to verify data

        except Exception as e:
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = {'Customer Name', 'Mobile No', 'Invoice No', 'Item Code', 'Receivable Value'}
        if not required_columns.issubset(df.columns):
            return Response({"error": "Invalid file format. Required columns missing."},
                            status=status.HTTP_400_BAD_REQUEST)

        for _, row in df.iterrows():
            DailySalesReport.objects.create(
                customer_name=row['Customer Name'],
                mobile_no=row['Mobile No'],  # Ensure 11-digit number with leading zero
                invoice_no=row['Invoice No'],
                item_code=row['Item Code'],
                receivable_value=row['Receivable Value']
            )

        return Response({"message": "Daily Sales Report uploaded successfully"}, status=status.HTTP_201_CREATED)


class UploadOutletInformationView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Allow file upload parsing

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith('.xlsx'):
            return Response({"error": "Only .xlsx files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read Excel file
            df = pd.read_excel(file, engine='openpyxl', dtype={'bm number': str})
            df['bm number'] = df['bm number'].astype(str).str.zfill(11)

            # Normalize column names (remove spaces and lowercase)
            df.columns = df.columns.str.strip().str.lower()

            # Required columns (matching your Excel file)
            required_columns = {'suffix', 'bm number'}

            if not required_columns.issubset(set(df.columns)):
                return Response({"error": "Invalid file format. Required 'Suffix' and 'BM Number' columns."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Save Outlet Information
            for _, row in df.iterrows():
                OutletManager.objects.update_or_create(
                    showroom_code=row['suffix'],  # Match "Suffix" column
                    defaults={'bm_number': row['bm number']}  # Match "BM Number" column
                )

            return Response({"message": "Outlet information uploaded successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:

            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# Generate OTP and send it to the customer
@api_view(['POST'])
def customer_list_create(request):
    mobile_no = request.data.get('mobile_no')
    customer_name = request.data.get('customer_name')

    # Step 1: Generate OTP and send it
    otp = generate_otp(mobile_no)

    # Step 2: Store OTP in the database (CustomerOTP model)
    # Use update_or_create to avoid duplicate key errors
    CustomerOTP.objects.update_or_create(
        mobile_no=mobile_no,
        defaults={'otp': otp}
    )

    # Step 3: Respond back with a message to verify OTP
    return Response(
        {"message": "OTP sent successfully, please verify."},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def verify_otp(request):
    mobile_no = request.data.get('mobile_no')
    entered_otp = request.data.get('otp')

    # Step 1: Validate input data
    if not mobile_no:
        return Response({"error": "mobile_no is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not entered_otp:
        return Response({"error": "otp is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Step 2: Check if the OTP exists for the given mobile_no
        otp_record = CustomerOTP.objects.get(mobile_no=mobile_no)

        # Step 3: Check if the OTP has expired (e.g., OTP valid for 5 minutes)
        otp_expiry_time = otp_record.created_at + timedelta(minutes=5)
        if timezone.now() > otp_expiry_time:
            otp_record.delete()  # Delete expired OTP
            return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Validate OTP (strip whitespace and ensure case-insensitive comparison)
        if otp_record.otp.strip() == entered_otp.strip():
            otp_record.delete()  # OTP is valid, delete it for security

            # Step 5: Create a customer (if OTP is correct)
            # Use only mobile_no for customer creation
            customer_data = {'mobile_no': mobile_no}
            serializer = CustomerSerializer(data=customer_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Customer verified and created successfully"},
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

    except CustomerOTP.DoesNotExist:
        return Response({"error": "OTP not found or expired"}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def discount_gift_list_create(request):
    if request.method == 'GET':
        discounts = DiscountGift.objects.all()
        serializer = DiscountGiftSerializer(discounts, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = DiscountGiftSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

import threading

def send_sms_async(mobile_no, message):
    """
    Send SMS in a separate thread.
    """
    def send_sms_task():
        try:
            from .modules import send_sms  # Import the send_sms function
            response = send_sms(mobile_no, message)
            if response.get("status") != "success":
                print(f"Failed to send SMS: {response}")  # Log the error
        except Exception as e:
            print(f"Error sending SMS: {e}")  # Log the exception

    # Start the SMS sending task in a new thread
    sms_thread = threading.Thread(target=send_sms_task)
    sms_thread.start()

@csrf_exempt
def redeem_discount(request):
    if request.method == 'POST':
        try:
            # Step 1: Parse the request data
            data = json.loads(request.body)
            mobile_no = data.get('mobile_no')
            discount_code = data.get('discount_code')

            # Step 2: Validate input data
            if not mobile_no:
                return JsonResponse({"error": "mobile_no is required"}, status=400)
            if not discount_code:
                return JsonResponse({"error": "discount_code is required"}, status=400)

            # Step 3: Check if the customer exists
            customer = Customer.objects.filter(mobile_no=mobile_no).first()
            if not customer:
                return JsonResponse({"error": "Customer not found"}, status=404)

            # Step 4: Check if the discount exists
            discount = DiscountGift.objects.filter(discount_code=discount_code).first()
            if not discount:
                return JsonResponse({"error": "Invalid discount code"}, status=400)

            # Step 5: Check if the customer has already redeemed a discount
            if DiscountRedemption.objects.filter(customer=customer).exists():
                return JsonResponse({"error": "Customer has already redeemed a discount!"}, status=400)

            # Step 6: Redeem the discount
            redemption = DiscountRedemption.objects.create(
                customer=customer,
                discount=discount,
                redeemed_at=now()
            )

            # Step 7: Send discount text to the customer via SMS (asynchronously)
            message = f"Congratulations! You have successfully redeemed the discount: {discount.discount_text}."
            send_sms_async(mobile_no, message)

            # Step 8: Return the redemption details
            serializer = DiscountRedemptionSerializer(redemption)
            return JsonResponse(serializer.data, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)