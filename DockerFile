# Use the official Python image from Docker Hub
FROM python:3.11

# Set environment variables that are needed during the build
# These are declared as ARG and will not persist in the final image
ARG OPENAI_API_KEY
ARG ACCOUNT_SID
ARG TWILLO_AUTH_TOKEN
ARG COUNTRY_CODE
ARG TWILIO_PHONE_NUMBER
ARG FCM_SERVER_KEY

# Set environment variables that will persist in the final image
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV ACCOUNT_SID=${ACCOUNT_SID}
ENV TWILLO_AUTH_TOKEN=${TWILLO_AUTH_TOKEN}
ENV COUNTRY_CODE=${COUNTRY_CODE}
ENV TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
ENV FCM_SERVER_KEY=${FCM_SERVER_KEY}


# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/


EXPOSE 8000

# Run collectstatic, migrate, and start the server
CMD ["sh", "-c", "python manage.py collectstatic --noinput&& python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
