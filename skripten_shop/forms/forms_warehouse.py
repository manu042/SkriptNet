# Django Packages
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password

# Third party packages
import re
import datetime
from captcha.fields import CaptchaField
