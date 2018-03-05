from django.contrib import admin
from django.urls import path, include
import debug_toolbar  # todo: debug mode only

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('debug/', include(debug_toolbar.urls))
]
