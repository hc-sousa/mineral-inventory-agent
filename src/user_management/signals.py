from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from allauth.account.models import EmailAddress

from django.conf import settings
if 'allauth.socialaccount' in settings.INSTALLED_APPS:
    from allauth.socialaccount.models import SocialAccount

import logging

logger = logging.getLogger(__name__)

@receiver(user_signed_up)
def populate_user_email_from_github(sender, request, user, **kwargs):
    social_account = SocialAccount.objects.filter(user=user, provider='github').first()
    if social_account:
        logger.debug(f"Extra data from GitHub: {social_account.extra_data}")
        # Attempt to retrieve emails from extra_data
        emails = social_account.extra_data.get('emails', [])

        if not emails:
            email = social_account.extra_data.get('email', None)
            if email:
                emails = [{'email': email, 'primary': True, 'verified': True}]

        logger.debug(f"Retrieved emails: {emails}")

        if isinstance(emails, list):
            primary_email = next((email for email in emails if email.get('primary') and email.get('verified')), None)
            if primary_email:
                user_email = primary_email['email']
                user.email = user_email
                user.save()

                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user_email,
                    defaults={'verified': True, 'primary': True}
                )