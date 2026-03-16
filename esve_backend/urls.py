from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/v1/auth/login/',   TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # Nos apps
    path('api/v1/clients/',    include('clients.urls')),
    path('api/v1/',            include('facturation.urls')),
    path('api/v1/',            include('commandes.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)