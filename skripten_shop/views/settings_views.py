# Django packages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

# My packages
from skripten_shop.models import ShopSettings
from skripten_shop.forms import SettingsForm, InfoTextForm
from skripten_shop.utilities import has_permisson_skriptenadmin, current_semester_is


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def shop_settings_view(request):
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
                return redirect(reverse('skripten_shop:shop-settings'))

    context = {
        'current_semester': current_semester_is,
        'info_text': shop_settings.info_text,
        'form': form,
    }

    return render(request, 'skripten_shop/settings_templates/settings.html', context)


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def edit_info_text_view(request):
    shop_settings = ShopSettings.objects.get(pk=1)

    if request.method == 'POST':

        form = InfoTextForm(request.POST)

        if form.is_valid():
            shop_settings.info_text = form.cleaned_data.get(('info_text'))
            shop_settings.save()
            return redirect(reverse('skripten_shop:shop-settings'))
    else:
        form = InfoTextForm(instance=shop_settings)

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/settings_templates/edit_info_text.html', context)
