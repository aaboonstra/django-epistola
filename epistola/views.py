# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'base.html'
