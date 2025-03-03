from django.shortcuts import render


from .modules import *
# Create your views here.



def generate_otp(mobile_no):
    """ Generate a 6-digit OTP and store it """
    otp = str(random.randint(100000, 999999))
    CustomerOTP.objects.update_or_create(mobile_no=mobile_no, defaults={'otp': otp})

    # Simulating OTP sending (Replace with SMS Gateway Integration)
    print(f"OTP sent to {mobile_no}: {otp}")

    return otp


class GenerateOTPView(APIView):
    """ Verify the customer purchase before sending OTP """
    def post(self, request):
        customer_name = request.data.get('customer_name')
        mobile_no = request.data.get('mobile_no')
        product_code = request.data.get('product_code')
        showroom_code = request.data.get('showroom_code')

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
    """ Show available gift cards with hidden names and allow customer selection """
    def get(self, request):
        gift_cards = GiftCard.objects.filter(is_active=True).values('product_code')
        return Response(gift_cards, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomerGiftSelectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Gift selected successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UploadDailySalesReportView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # ✅ Add parsers for file upload

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith('.xlsx'):
            return Response({"error": "Only .xlsx files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, engine='openpyxl')
        except Exception as e:
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate required columns
        required_columns = {'Customer Name', 'Mobile No', 'Invoice No', 'Item Code', 'Receivable Value'}
        if not required_columns.issubset(df.columns):
            return Response({"error": "Invalid file format. Required columns missing."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Process and save data
        for _, row in df.iterrows():
            DailySalesReport.objects.create(
                customer_name=row['Customer Name'],
                mobile_no=row['Mobile No'],
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
            df = pd.read_excel(file, engine='openpyxl')

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
