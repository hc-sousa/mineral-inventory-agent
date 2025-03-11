from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserPayment(models.Model):
    app_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL) 
    email = models.EmailField(null=True, blank=True) 
    payment_bool = models.BooleanField(default=False)

    stripe_checkout_id = models.CharField(max_length=500)

@receiver(post_save, sender=User)
def create_user_payment(sender, instance, created, **kwargs):
    if created:
        UserPayment.objects.create(app_user=instance)