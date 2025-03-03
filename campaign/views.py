from django.shortcuts import render
from .modules import *
# Create your views here.

class GenerateOTPView(APIView):
    def post(self, request):
        mobile_no = request.data.get('mobile_no')
        otp = str(random.randint(100000, 999999))
        CustomerOTP.objects.update_or_create(mobile_no=mobile_no, defaults={'otp': otp})

        # Simulating OTP sending (Integrate with SMS Gateway here)
        print(f"OTP sent to {mobile_no}: {otp}")

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
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
    def get(self, request):
        gift_cards = GiftCard.objects.filter(is_active=True).values('product_code')
        return Response(gift_cards, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomerGiftSelectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Gift selected successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UploadSalesReportView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(file.name, file)
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            if row['Receivable Value'] >= 5000:
                DailySalesReport.objects.create(
                    customer_name=row['Customer Name'],
                    mobile_no=row['Mobile No'],
                    invoice_no=row['Invoice No'],
                    item_code=row['Item Code'],
                    receivable_value=row['Receivable Value']
                )
        return Response({"message": "Sales report uploaded successfully"}, status=status.HTTP_201_CREATED)