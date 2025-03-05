
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




class GenerateOTPView(APIView):
    """ Verify the customer purchase before sending OTP """
    def post(self, request):
        customer_name = request.data.get('customer_name')
        mobile_no = request.data.get('mobile_no')
        product_code = request.data.get('product_code')
        invoice_no = request.data.get('invoice_no')

        # Check if the customer exists in DailySalesReport and is eligible
        sales_record = DailySalesReport.objects.filter(
            mobile_no=mobile_no, item_code=product_code
        ).first()

        if not sales_record:
            return Response({"error": "Purchase not found"}, status=status.HTTP_404_NOT_FOUND)

        if not sales_record.is_eligible():
            return Response({"error": "Not eligible for the campaign"}, status=status.HTTP_403_FORBIDDEN)

        # Generate OTP and send it
        generate_otp(mobile_no)
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)




class VerifyOTPView(APIView):
    """ Verify the OTP sent to the customer """
    def post(self, request):
        mobile_no = request.data.get('mobile_no')
        entered_otp = request.data.get('otp')

        try:
            otp_record = CustomerOTP.objects.get(mobile_no=mobile_no)
            if otp_record.otp == entered_otp:
                otp_record.delete()
                return Response({"message": "OTP verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomerOTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND)


class GiftSelectionView(APIView):
    """ Show available gift cards and allow a one-time customer selection """

    def get(self, request):
        gift_cards = GiftCard.objects.filter(is_active=True).values('product_code')
        return Response(gift_cards, status=status.HTTP_200_OK)

    def post(self, request):
        mobile_no = request.data.get('mobile_no')
        product_code = request.data.get('product_code')

        # Check if the customer has already selected a gift
        if CustomerGiftSelection.objects.filter(mobile_no=mobile_no).exists():
            return Response({"error": "Gift already selected. You cannot select again."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Ensure product_code is stored properly
        try:
            gift_card = GiftCard.objects.get(product_code=product_code)
        except GiftCard.DoesNotExist:
            return Response({"error": "Invalid product code."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomerGiftSelectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(gift_card=gift_card)  # Store gift_card correctly
            return Response({"message": "Gift selected successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"error": "Invalid file format. Required columns missing."}, status=status.HTTP_400_BAD_REQUEST)

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