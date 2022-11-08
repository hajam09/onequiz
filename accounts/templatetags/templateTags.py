from django import template
from django.urls import reverse

from onequiz.base.utils.navigationBar import linkItem, Icon

register = template.Library()


@register.simple_tag
def navigationPanel(request):
    links = [
        linkItem('Home', '', None),
    ]

    if request.user.is_authenticated:
        links.append(
            linkItem('Account', '', None, [
                None,
                linkItem('Logout', reverse('accounts:logout'), Icon('', 'fas fa-sign-out-alt', '15')),
            ]),
        )
    else:
        links.append(
            linkItem('Login / Register', '', None, [
                linkItem('Register', reverse('accounts:register'), Icon('', 'fas fa-user-circle', '20')),
                None,
                linkItem('Login', reverse('accounts:login'), Icon('', 'fas fa-sign-in-alt', '20')),
            ]),
        )
    return links
