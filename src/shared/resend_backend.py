# shared/resend_backend.py

import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

import logging

class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for message in email_messages:
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {settings.RESEND_API_KEY}',
                    'Content-Type': 'application/json',
                },
                json={
                    'from': message.from_email,
                    'to': message.to,
                    'subject': message.subject,
                    'text': message.body,
                    'html': message.alternatives[0][0] if message.alternatives else None,
                },
            )
            if response.status_code != 200:
                # Log error
                logging.error(f"Failed to send email: {response.json()}")
                
            else:
                logging.info(f"Successfully sent email to {message.to}")
