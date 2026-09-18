from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns


# yasg
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apis import views
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


router = routers.SimpleRouter()
router.register(r'movies', views.MovieViewSet, basename="movie")
router.register(r'cinemas', views.CinemaViewSet, basename="cinema")
router.register(r'cinemahalls', views.CinemaHallViewSet, basename="cinemahall")


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path("api/", include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', views.ProfileGetView.as_view(), name="profile"),
    path('api/show/reserve/', views.ReserveShowView.as_view(), name="show_reservation"),
] 

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("cine-admin/", include("cine_admin.urls")),
    path("accounts/", include("accounts.urls")),
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
