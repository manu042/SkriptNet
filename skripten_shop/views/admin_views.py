# Django Packages
from django.shortcuts import render
from django.conf import settings

# Third party packages
import os


def show_logfile_view(request):
    # logfile_text = open(settings.BASE_DIR + '/logfiles/skripten_shop.log', 'r').read()

    with open(settings.BASE_DIR + '/logfiles/skripten_shop.log', 'r') as f:
        logfile_text = f.read()

    if logfile_text is '':
        logfile_text = False

    context = {
        'logfile_text': logfile_text,
    }

    return render(request, 'skripten_shop/admin_templates/show_logfile.html', context)
