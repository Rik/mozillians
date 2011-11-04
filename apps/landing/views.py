import jingo

from django.http import HttpResponse

from session_csrf import anonymous_csrf

@anonymous_csrf
def about(request):
    return jingo.render(request, 'landing/about.html')

@anonymous_csrf
def home(request):
    return jingo.render(request, 'landing/home.html')


def robots(request):
    return HttpResponse("""User-agent: *\nDisallow: /\n""",
                        mimetype="text/plain")


def confirm_register(request):
    return jingo.render(request, 'landing/confirm_register.html',
                        dict())
