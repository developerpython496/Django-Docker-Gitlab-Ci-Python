from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsTeamOwner
from workspace.models import Workspace
from workspace.serializers import WorkspaceSerializer

from workspace.services import WorkspaceService


class WorkspaceViewSet(viewsets.GenericViewSet):
    """
        API endpoints for managing workspaces.
    """
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsTeamOwner]
        return super(WorkspaceViewSet, self).get_permissions()

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Workspace.objects.none()
        if hasattr(self.request.user, "owned_team"):
            return Workspace.objects.filter(team=self.request.user.owned_team)
        return Workspace.objects.filter(users__in=[self.request.user])

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset().filter(pk=pk)
        if not queryset.exists():
            return Response({'detail': 'Workspace not found.'}, status=status.HTTP_404_NOT_FOUND)

        workspace = queryset.first()
        serializer = self.get_serializer(workspace)
        return Response(serializer.data)

    def create(self, request):
        team_id = request.user.owned_team.id
        name = request.data['name']

        success, workspace, message = WorkspaceService.create_workspace(team_id, name)
        if success:
            serializer = self.get_serializer(workspace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'detail': message}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        new_name = request.data['name']

        success, workspace, message = WorkspaceService.update_workspace_name(pk, new_name)
        if success:
            serializer = self.get_serializer(workspace)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': message}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        success, message = WorkspaceService.delete_workspace(pk)
        if success:
            return Response({'detail': message}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': message}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'], url_path='user-add', url_name='user-add',
            permission_classes=[IsAuthenticated, IsTeamOwner])
    def add_user(self, request, *args, **kwargs):
        pk = self.get_object().id
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        success, workspace_role, message = WorkspaceService.add_user_to_workspace(pk, user_id, role)
        if success:
            return Response({'detail': message}, status=status.HTTP_200_OK)
        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='user-remove', url_name='user-remove',
            permission_classes=[IsAuthenticated, IsTeamOwner])
    def remove_user(self, request, *args, **kwargs):
        workspace_role_id = request.data.get('workspace_role_id')

        success, message = WorkspaceService.remove_user_from_workspace(workspace_role_id)

        if success:
            return Response({'detail': message}, status=status.HTTP_200_OK)
        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='user-update-role', url_name='user-update-role',
            permission_classes=[IsAuthenticated, IsTeamOwner])
    def update_user_role(self, request, *args, **kwargs):
        workspace_role_id = request.data.get('workspace_role_id')
        role = request.data.get('role')

        success, workspace_role, message = WorkspaceService.update_user_role_in_workspace(workspace_role_id, role)

        if success:
            return Response({'detail': message}, status=status.HTTP_200_OK)
        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
