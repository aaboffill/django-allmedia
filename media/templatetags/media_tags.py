# coding=utf-8
from allauth.socialaccount.models import SocialToken
from django import template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

register = template.Library()


@register.assignment_tag
def get_google_social_token(user):
    if not user or not isinstance(user, User):
        return None

    try:
        return SocialToken.objects.get(
            app__provider='google',
            app__sites=Site.objects.get_current(),
            account__provider='google',
            account__user=user
        )
    except SocialToken.DoesNotExist:
        return None