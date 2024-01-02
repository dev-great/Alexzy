# accounts/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

from authentication.models import CustomUser


class EmailModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(
            f"Attempting to authenticate user with email: {username} {password}")
        UserModel = get_user_model()

        try:
            user = CustomUser.objects.get(email=username)
        except UserModel.DoesNotExist:
            # User does not exist
            return None

        # Check the password
        if check_password(password, user.password):
            # You can include additional checks here if needed

            # Check if the user is active
            if user.is_active:
                return user
            else:
                # User is not active, raise a ValidationError
                raise ValidationError(
                    "This account has been deactivated. Please contact the account administrator.")
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            # User does not exist
            return None
