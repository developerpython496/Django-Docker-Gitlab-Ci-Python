from dj_rest_auth.views import PasswordResetConfirmView
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Social Media Automation Platform API",
        default_version='v1',
        description="API for Social Media Automation Platform",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),

    path('auth/password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('auth/', include('dj_rest_auth.urls')),

    path('', include("core.urls")),  # registration
    path('workspace/', include("workspace.urls")),
    path('subscription/', include("subscription.urls")),
    path('social-media/', include("social_media.urls")),
]
