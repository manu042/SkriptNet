# Django packages
from django.shortcuts import render

# My packages
from skripten_shop.models import CurrentSemester, ShopSettings
from skripten_shop.forms import SettingsForm


def shop_settings_view(request):
    current_semester = CurrentSemester.objects.get(pk=1)
    shop_settings = ShopSettings.objects.get(pk=1)

    form = SettingsForm(instance=shop_settings)

    if request.method == 'POST':

        if 'start_new_semester' in request.POST:
            print('start_new_semester')

        if 'save_settings' in request.POST:
            form = SettingsForm(request.POST)

            if form.is_valid():
                shop_settings.state = form.cleaned_data.get('state')
                shop_settings.max_article = form.cleaned_data.get('max_article')
                shop_settings.days_reserved = form.cleaned_data.get('days_reserved')
                shop_settings.save()

    context = {
        'current_semester': current_semester,
        'form': form,
    }

    return render(request, 'skripten_shop/settings_templates/settings.html', context)
