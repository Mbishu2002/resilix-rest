# utils.py

from pyfcm import FCMNotification
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

def send_push_notification(registration_ids, message_title, message_body):
    """
    Sends a push notification to the given registration IDs using FCM.
    """
    push_service = FCMNotification(api_key=settings.fcm_server_key)
    result = push_service.notify_multiple_devices(
        registration_ids=registration_ids,
        message_title=message_title,
        message_body=message_body
    )
    return result


def send_sms_notification(phone_number, message):
    """
    Sends an SMS notification to the given phone number using Twilio.
    """
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    client.messages.create(
        body=message,
        from_=settings.twilio_phone_number,
        to=phone_number,
    )
