from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"Attempting to authenticate user with email: {username}")
        try:
            user = User.objects.get(email=username)
            print(f"User found: {user}")
            if user.check_password(password):
                print("Password check successful")
                return user
            else:
                print("Password incorrect")
                return None
        except User.DoesNotExist:
            print(f"User with email {username} does not exist")
            return None
