import os
import json
import requests
from pyfcm import FCMNotification
from django.conf import settings
from twilio.rest import Client
import pyotp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import (
    AlertSerializer,
    DisasterFeedbackSerializer,
    LocationSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    AlertChoicesSerializer,
    ChatMessageSerializer,
)
from .models import Alert, DisasterFeedback, Location, AlertChoices, CustomUser
from rest_framework.authtoken.models import Token
from .serializers import ChatMessageSerializer
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

def fetch_service_account_file(url):
    response = requests.get(url)
    response.raise_for_status()  
    return response.json()

def initialize_fcm():
    service_account_url = settings.FCM_SERVICE_ACCOUNT_URL  
    service_account_info = fetch_service_account_file(service_account_url)
    project_id = service_account_info.get("project_id")
    return FCMNotification(service_account_file=None, credentials=service_account_info, project_id=project_id)

fcm = initialize_fcm()

def send_push_notification(registration_ids, message_title, message_body):
    if registration_ids:
        result = fcm.notify_multiple_devices(
            registration_ids=registration_ids,
            message_title=message_title,
            message_body=message_body
        )
        return result
    return None

def send_sms_notification(phone_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number,
    )

def send_notifications(user, message_title, message_body):
    fcm_token = user.fcm_token
    phone_number = user.phone_number
    
    if fcm_token:
        send_push_notification([fcm_token], message_title, message_body)
    else:
        if phone_number:
            send_sms_notification(phone_number, message_body)

def send_sms_code(user):
    time_otp = pyotp.TOTP(user.otp, interval=300)
    otp_code = time_otp.now()
    user_phone_number = user.phone_number

    send_sms_notification(user_phone_number, "Your verification code is " + otp_code)

def verify_phone(user, sms_code):
    code = int(sms_code)
    if user.authenticate(code):
        user.phone_number_verified = True
        user.save()
        return True
    return False

class UserRegistration(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            user = serializer.save()
            send_notifications(user, "Welcome!", "Thanks for registering with our app.")
            
            try:
                send_sms_code(user)
            except Exception as e:
                # Log the error message if needed
                # logger.error(f"Failed to send SMS: {e}")
                return Response({
                    "message": "Registration successful, but failed to send SMS. Please verify your account manually."
                }, status=status.HTTP_201_CREATED)
                
            return Response({
                "message": "Registration successful. Please verify your account using the OTP sent to your phone number."
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class VerifyPhoneView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('otp_code')

        print(f"phone_number: {phone_number}, otp_code: {otp_code}")

        if not phone_number or not otp_code:
            return Response(
                {"detail": "Phone number and OTP code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User with this phone number does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if verify_phone(user, otp_code):
            return Response(
                {"message": "Phone number verified successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid OTP code."},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserLogin(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key, "username": user.username}, status=status.HTTP_200_OK)
        return Response({"detail": "Authentication failed."}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        content = {"user": str(request.user), "auth": str(request.auth)}
        return Response(data=content, status=status.HTTP_200_OK)

class ListDisasterFeedback(APIView):
    def get(self, request):
        disaster_feedback = DisasterFeedback.objects.all()
        serializer = DisasterFeedbackSerializer(disaster_feedback, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DisasterFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListLocations(APIView):
    def get(self, request):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmergencyAlertChoicesView(APIView):
    def get(self, request):
        emergency_choices = AlertChoices.objects.all()
        serializer = AlertChoicesSerializer(emergency_choices, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AlertChoicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AlertListCreateView(generics.ListCreateAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

    def perform_create(self, serializer):
        user_location_data = self.request.data.get("user_location", None)

        if user_location_data:
            location_serializer = LocationSerializer(data=user_location_data)
            if location_serializer.is_valid():
                location_instance = location_serializer.save()
                serializer.validated_data["location"] = location_instance

        alert_instance = serializer.save()
        alert_description = alert_instance.description
        first_aid_response = serializer.get_first_aid_response(alert_description)

        alert_instance.first_aid_response = first_aid_response
        alert_instance.save()

        if self.request.data.get("broadcast_to_all", False):
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "alerts",
                {
                    "type": "alert",
                    "message": f"New alert: {alert_instance.description}"
                }
            )

            users = CustomUser.objects.all()
            for user in users:
                message_title = "New Alert"
                message_body = alert_instance.description
                send_notifications(user, message_title, message_body)

        return alert_instance

class ChatbotAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.validated_data['message']
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                prompt = f"User: {user_message}\nBot:"

                response = model.generate_content(prompt)
                bot_response = response.text
                return Response({'response': bot_response}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

