import stripe
from django.shortcuts import render

from src import settings

def index(request):
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        coupon = stripe.Coupon.retrieve(settings.COUPON_ID)
        total_coupons = coupon.get('max_redemptions')
        coupons_left = total_coupons - coupon.get('times_redeemed')
    except stripe.InvalidRequestError:
        coupons_left = 0
        total_coupons = 0

    return render(request, 'landing_page/index.html', {'coupons_left': coupons_left, 'total_coupons': total_coupons})