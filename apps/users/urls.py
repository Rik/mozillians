from django.conf.urls.defaults import patterns, url

from django.contrib.auth import views as auth_views

from jinjautils import jinja_for_django

from . import views

# So we can use the contrib logic for password resets, etc.
auth_views.render_to_response = jinja_for_django


urlpatterns = patterns('',
    url(r'^logout$', auth_views.logout, dict(redirect_field_name='next'),
        name='logout'),

    url(r'^register$', views.register, name='register'),
    url(r'^confirm$', views.confirm, name='confirm'),
    url(r'^send_confirmation$', views.send_confirmation,
        name='send_confirmation'),

    url(r'^password_reset_confirm/'
         '(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-'
         '[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm,
        name='password_reset_confirm'),
)
