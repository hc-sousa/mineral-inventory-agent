from django.contrib import admin
from .models import UserPayment

@admin.register(UserPayment)
class UserPaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserPayment._meta.fields]