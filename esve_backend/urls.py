from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from facturation.views import dashboard_stats

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/v1/auth/login/',   TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # Comptes
    path('api/v1/auth/', include('comptes.urls')),

    # Apps
    path('api/v1/', include('clients.urls')),
    path('api/v1/', include('facturation.urls')),
    path('api/v1/', include('commandes.urls')),

    # Dashboard
    path('api/v1/dashboard/stats/', dashboard_stats, name='dashboard-stats'),

    path('api/v1/comptes/', include('comptes.urls')),  # ← AJOUTÉ

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)