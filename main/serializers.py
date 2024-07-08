from rest_framework import serializers
from .models import Alert, DisasterFeedback, Location, CustomUser, AlertChoices
from rest_framework.validators import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
import openai
from django.conf import settings
import google.generativeai as genai
import markdown
import textwrap

genai.configure(api_key=settings.GOOGLE_API_KEY)

def to_markdown(text):
    text = text.replace('•', '  *')
    return markdown.markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

class AlertSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Alert
        fields = ["alert_type", "description", "location", "first_aid_response"]

    
class DisasterFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterFeedback
        fields = ["description", "date_time_of_feedback", "alert"]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["longitude", "latitude"]

    def create(self, validated_data):
        return Location.objects.create(**validated_data)

class AlertChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertChoices
        fields = ["id", "emergency_name"]

CustomUser = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=15, required=True)  # Phone number is required
    fcm_token = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ["username", "phone_number", "password", "fcm_token"]

    def validate(self, attrs):
        if CustomUser.objects.filter(username=attrs["username"]).exists():
            raise ValidationError("Username Already Taken")
        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")
        fcm_token = validated_data.pop("fcm_token", None)

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        Token.objects.create(user=user)

        if fcm_token:
            user.fcm_token = fcm_token
            user.save()

        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User is not active.")
                data["user"] = user
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
        else:
            raise serializers.ValidationError(
                "Must include 'username' and 'password' fields."
            )

        return data

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
