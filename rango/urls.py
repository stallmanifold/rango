from django.conf.urls    import include, url
from django.conf         import settings
from django.views.static import serve
from rango               import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^rango/category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    #url(r'^register/$', views.register, name='register'),
    #url(r'^login/$', views.user_login, name='login'),
    url(r'^restricted/$', views.restricted, name='restricted'),
    #url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^change_password/password_change_complete/$', views.password_change_complete, name='password_change_complete'),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, { 
            'document_root': settings.MEDIA_ROOT,
        }),
    ]