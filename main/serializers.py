from rest_framework import serializers
from .models import Alert, DisasterFeedback, Location, CustomUser, AlertChoices
from rest_framework.validators import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
import openai
from django.conf import settings

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["alert_type", "description", "location"]

    def get_first_aid_response(self, alert_description):
        openai.api_key = settings.OPENAI_API_KEY
        prompt = (
            f"Given the following emergency alert: {alert_description}, "
            "You are well-versed in first aid measures for emergencies in Cameroon. "
            "Provide immediate and clear first aid measures. Offer concise and effective first aid guidance."
        )

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
        )

        return response.choices[0].text.strip()

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
        fields = ["emergency_name"]

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
