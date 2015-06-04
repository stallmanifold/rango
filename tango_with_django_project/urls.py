from django.conf.urls                   import include, url
from django.contrib                     import admin
from registration.backends.simple.views import RegistrationView


# Create a new class that redirects the user to the index page, if successful at logging
class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return '/rango/add_profile'


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
    url(r'^$'     , 'rango.views.index', name='index'),
    #Add in this url pattern to override the default pattern in accounts.
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
]
