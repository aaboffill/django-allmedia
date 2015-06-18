# coding=utf-8
from allauth.socialaccount.models import SocialToken
from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.assignment_tag
def get_google_social_token(user):
    if not user or not isinstance(user, User):
        return None

    try:
        return SocialToken.objects.filter(app__provider='google', account__provider='google', account__user=user).get()
    except SocialToken.DoesNotExist:
        return None