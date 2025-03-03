import random
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from Utility.otp_handler import *
import pandas as pd
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser
