import random
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import pandas as pd
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser
from openpyxl import load_workbook
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from rest_framework.parsers import FormParser
import random
from Utility.smsHandlers import send_sms
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta
