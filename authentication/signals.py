
from .models import *
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.conf import settings
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


@receiver(post_save, sender=User)
def create_referral_code(sender, instance, created, **kwargs):
    if created:
        ReferralCode.objects.create(user=instance, code=123)


# # USER REFERRAL BONUS
# @ receiver(post_save, sender=Referral)
# def create_referral_bonus(sender, instance, *args, **kwargs):
#     if instance:
#         if instance:
#             user_obj = WalletModel.objects.get(
#                 user_id__exact=instance.referred_by)
#     new = user_obj.balance + 2
#     user_obj.balance = new
#     user_obj.save()


# PASSWORD RESET EMAIL
@ receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    inshopper_user = instance
    merge_data = {
        'inshopper_user':  f"{reset_password_token.user.email}",
        'otp': f" {reset_password_token.key} "
    }
    html_body = render_to_string("emails/otp_mail.html", merge_data)
    msg = EmailMultiAlternatives(subject="inshopper Password Reset Token", from_email=settings.EMAIL_HOST_USER, to=[
                                 reset_password_token.user.email], body=" ",)
    msg.attach_alternative(html_body, "text/html")
    return msg.send(fail_silently=False)
