# Django packages
from django.shortcuts import render

# My packages
from skripten_shop.models import CurrentSemester, ShopSettings
from skripten_shop.forms import SettingsForm


def shop_settings(request):
    current_semester = CurrentSemester.objects.get(pk=1)
    shop_settings = ShopSettings.objects.get(pk=1)

    if request.method == 'GET':
        form = SettingsForm(instance=shop_settings)
    else:
        form = SettingsForm()

    context = {
        'current_semester': current_semester,
        'form': form,
    }

    return render(request, 'skripten_shop/settings_templates/settings.html', context)
