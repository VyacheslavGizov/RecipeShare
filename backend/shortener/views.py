from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from .models import LinkKey


class RedirectView(View):

    def get(self, request, *args, **kwargs):
        return redirect(get_object_or_404(LinkKey, key=kwargs['url_key']).link)
