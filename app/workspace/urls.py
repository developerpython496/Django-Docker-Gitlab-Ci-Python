from rest_framework.routers import DefaultRouter

from workspace.views import WorkspaceViewSet

router = DefaultRouter()
router.register('', WorkspaceViewSet, basename='workspace')

app_name = "workspace"
urlpatterns = [] + router.urls
