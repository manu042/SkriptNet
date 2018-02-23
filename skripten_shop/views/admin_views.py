# Django Packages
from django.views import View
from django.conf import settings
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin


@method_decorator(login_required, name='dispatch')
class LogfileView(UserPassesTestMixin, View):

    def get(self, request, *args, **kwargs):
        with open(settings.BASE_DIR + '/logfiles/skripten_shop.log', 'r') as f:
            logfile_text = f.read()

        if logfile_text is '':
            logfile_text = False

        return render(request, 'skripten_shop/admin_templates/show_logfile.html', {'logfile_text': logfile_text,})

    def test_func(self):
        """
        Prüfen, ob der User die Berechtigung für diese Seite hat
        """
        return self.request.user.groups.filter(name='Admin').exists()
