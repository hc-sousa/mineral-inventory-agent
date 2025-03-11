import json
import os
import logging
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

from django.conf import settings
import stripe

from stripe_payments.models import UserPayment

logger = logging.getLogger(__name__)

def send_purchase_email(email, host = 'localhost:8000'):
    # You can change the email subject and message to your liking on stripe_payments/data/product_bought_email.json
    with open(os.path.join(settings.BASE_DIR, 'stripe_payments', 'data', 'product_bought_email.json')) as email_data_file:
        email_data = json.load(email_data_file)
        subject = email_data['subject']
        message = email_data['message'].replace("{__user_email__}", email).replace("{__url__}", host)
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently = not settings.DEBUG,
    )

def payment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=settings.PAYMENT_METHODS,
        line_items=[
            {
                'price': settings.PRODUCT_PRICE_ID,
                'quantity': 1,
            },
        ],
        mode='payment',
        customer_creation='always',
        success_url=settings.REDIRECT_DOMAIN + '/successful?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=settings.REDIRECT_DOMAIN + '/cancelled',
        discounts=[{'coupon': settings.COUPON_ID}],
    )
    # Cria o UserPayment associado ao usuário e ao checkout session
    UserPayment.objects.create(
        app_user=request.user if request.user.is_authenticated else None,
        email=request.user.email if request.user.is_authenticated else None,
        stripe_checkout_id=checkout_session.id,
        payment_bool=False
    )
    return redirect(checkout_session.url, code=303)

def success(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get('session_id', None)
    if checkout_session_id is None:
        return HttpResponse(status=400)

    try:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer_email = session.customer_details.email

        # Update or create the UserPayment with the email
        user_payment, created = UserPayment.objects.update_or_create(
            stripe_checkout_id=checkout_session_id,
            defaults={
                'email': customer_email,
                'payment_bool': True
            },
        )
        
        send_purchase_email(customer_email, host=request.get_host())

        return render(request, 'stripe_payments/success.html', {'customer_email': customer_email})
    except UserPayment.DoesNotExist:
        logger.error(f"UserPayment not found for session_id: {checkout_session_id}")
        return HttpResponse(status=404)
    except Exception as e:
        logger.error(f"Error retrieving Stripe session: {e}")
        return HttpResponse(status=500)

def cancel(request):
    return render(request, 'stripe_payments/cancelled.html')

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        if session_id:
            try:
                user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
                line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
                user_payment.payment_bool = True
                user_payment.save()
                logger.info(f"Payment processed for session: {session_id}")
            except UserPayment.DoesNotExist:
                logger.error(f"UserPayment not found for session_id: {session_id}")
                return HttpResponse(status=404)
            except Exception as e:
                logger.error(f"Error processing payment: {e}")
                return HttpResponse(status=500)
        else:
            logger.error("Session ID not found in webhook payload")
            return HttpResponse(status=400)

    return HttpResponse(status=200)