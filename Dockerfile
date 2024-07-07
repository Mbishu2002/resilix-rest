# Use the official Python image from Docker Hub
FROM python:3.11

# Set environment variables that are needed during the build
# These are declared as ARG and will not persist in the final image
ARG GOOOGLE_API_KEY
ARG ACCOUNT_SID
ARG REDIS_URL
ARG TWILIO_AUTH_TOKEN
ARG COUNTRY_CODE
ARG TWILIO_PHONE_NUMBER
ARG FCM_SERVER_KEY

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV GOOOGLE_API_KEY=${GOOOGLE_API_KEY}
ENV ACCOUNT_SID=${ACCOUNT_SID}
ENV REDIS_URL=${REDIS_URL}
ENV TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
ENV COUNTRY_CODE=${COUNTRY_CODE}
ENV TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
ENV FCM_SERVER_KEY=${FCM_SERVER_KEY}

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port on which the app will run
EXPOSE 8000

# Run collectstatic, makemigrations, migrate, and start the server
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
