from pyfcm import FCMNotification
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

def send_push_notification(registration_ids, message_title, message_body):
    """
    Sends a push notification to the given registration IDs using FCM.

    Args:
        registration_ids (list): List of device registration IDs to send the notification to.
        message_title (str): Title of the push notification.
        message_body (str): Body text of the push notification.

    Returns:
        dict: Result of the notification request.
    """
    try:
        push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)
        result = push_service.notify_multiple_devices(
            registration_ids=registration_ids,
            message_title=message_title,
            message_body=message_body
        )
        return result
    except Exception as e:
        print(f"Error sending push notification: {str(e)}")
        return {"success": 0, "error": str(e)}

def send_sms_notification(phone_number, message):
    """
    Sends an SMS notification to the given phone number using Twilio.

    Args:
        phone_number (str): The recipient's phone number.
        message (str): The SMS message to send.

    Returns:
        dict: Result of the SMS request.
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_response = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )
        return {"sid": message_response.sid, "status": message_response.status}
    except TwilioException as e:
        print(f"Error sending SMS notification: {str(e)}")
        return {"success": 0, "error": str(e)}
