from django.conf.urls        import include, url
from django.conf             import settings
from django.views.static     import serve
from django.conf.urls.static import static
from rango                   import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^rango/category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    url(r'^restricted/$', views.restricted, name='restricted'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^change_password/password_change_complete/$', views.password_change_complete, 
        name='password_change_complete'),
    url(r'^goto/(?P<page_id>[0-9]+)/$', views.track_url, name='goto'),
    url(r'^add_profile/registration_complete/$', views.registration_complete, 
        name='registration_complete'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/edit_profile/$', views.edit_profile, name='edit_profile'),
    url(r'^profile/edit_profile/profile_edit_complete/$', views.profile_edit_complete, 
        name='profile_edit_complete'),
    url(r'^search/$', views.search, name='search'),
]

# Do not use this for production!
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, { 
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

    # Do not use this for production!
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)