from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from skripten_shop.models import Professor, Skript


def prof_login_view(request, key):
    #print(key)
    #print( login_prof(key, request))
    if login_prof(key, request):
        return HttpResponseRedirect("/prof/overview/")
    #print(request.sessions)
    return HttpResponse("login failed");

def login_prof(key, request):
    #check weather login key is valid
    prof = Professor.objects.filter(authentication_key=key)
    print(len(prof))
    #print(request.session['prof_authenticated'])
    if (len(prof) == 1):
        print(prof[0])
        prof_id = prof[0].pk
    else:
        print("Ungültiger Key")
        return False
    #store login to session
    #if 'prof_authenticated' not in request.session:
    request.session['prof_authenticated'] = prof_id
    return True
    #else:
    #print("already has key")
    #return False


def is_prof_authenticated(request):
    if ('prof_authenticated' in request.session):
        return request.session['prof_authenticated']
    return False

def prof_overview(request):
    print(is_prof_authenticated(request))
    if(not is_prof_authenticated(request)):
        return HttpResponse("Access denied")

    context = {
        'prof': Professor.objects.get(pk=request.session['prof_authenticated']),
        'view_skript': Skript.objects.filter(author__pk=request.session['prof_authenticated']),
        'editable': False,
    }
    return render(request, 'skripten_shop/prof_templates/prof_overview.html', context)
