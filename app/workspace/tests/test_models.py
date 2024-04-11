import pytest
from django.core.exceptions import ValidationError

from core.models import Team
from workspace.models import Workspace, WorkspaceRole, Role

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_workspace_positive():
    user = User.objects.create_user(email="test@example.com", password="testpassword")
    team = Team.objects.create(name="Test Team", owner=user)
    workspace = Workspace.objects.create(name="Test Workspace", team=team)
    assert workspace.name == "Test Workspace"


@pytest.mark.django_db
def test_create_workspace_negative():
    user = User.objects.create_user(email="test@example.com", password="testpassword")
    team = Team.objects.create(name="Test Team", owner=user)
    workspace = Workspace.objects.create(name="Test Workspace", team=team)
    with pytest.raises(ValidationError):
        workspace.team = Team.objects.create(name="Another Team",
                                             owner=User.objects.create_user(email="another@example.com",
                                                                            password="testpassword"))
        workspace.save()


@pytest.mark.django_db
def test_create_workspace_role_positive():
    user = User.objects.create_user(email="test@example.com", password="testpassword")
    user1 = User.objects.create_user(email="test1@example.com", password="testpassword")
    team = Team.objects.create(name="Test Team", owner=user)
    workspace = Workspace.objects.create(name="Test Workspace", team=team)
    workspace_role = WorkspaceRole.objects.create(role=Role.CONTENT_CREATOR, workspace=workspace, user=user1)
    assert workspace_role.role == Role.CONTENT_CREATOR
    assert workspace_role.workspace == workspace
    assert workspace_role.user == user1


@pytest.mark.django_db
def test_create_workspace_role_negative():
    user = User.objects.create_user(email="test@example.com", password="testpassword")
    team = Team.objects.create(name="Test Team", owner=user)
    workspace = Workspace.objects.create(name="Test Workspace", team=team)

    with pytest.raises(ValidationError):
        WorkspaceRole.objects.create(role=Role.CONTENT_CREATOR, workspace=workspace, user=user)
