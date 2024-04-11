import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from workspace.models import WorkspaceRole
from social_media.models import SocialMediaPlatform, InstagramAccount

User = get_user_model()


@pytest.mark.django_db
class TestWorkspaceViewSet:
    def test_list_workspaces_as_owner(self, user, team, workspace):
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('workspace:workspace-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Test Workspace'

    def test_list_workspaces_as_team_member(self, user, team, workspace):
        team_member = User.objects.create_user(email='member@example.com', password='testpassword')
        workspace.users.add(team_member)

        client = APIClient()
        client.force_authenticate(user=team_member)

        url = reverse('workspace:workspace-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Test Workspace'

    def test_list_workspaces_unauthenticated(self, user, team, workspace):
        client = APIClient()

        url = reverse('workspace:workspace-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_non_member_workspace(self, user, team, workspace):
        non_member = User.objects.create_user(email='nonmember@example.com', password='testpassword')

        client = APIClient()
        client.force_authenticate(user=non_member)

        url = reverse('workspace:workspace-detail', kwargs={'pk': workspace.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_workspace_as_non_owner(self, user, team, workspace):
        non_owner = User.objects.create_user(email='nonowner@example.com', password='testpassword')

        client = APIClient()
        client.force_authenticate(user=non_owner)

        url = reverse('workspace:workspace-list')
        response = client.post(url, data={'name': 'New Workspace'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_workspace_as_non_owner(self, user, team, workspace):
        non_owner = User.objects.create_user(email='nonowner@example.com', password='testpassword')

        client = APIClient()
        client.force_authenticate(user=non_owner)

        url = reverse('workspace:workspace-detail', kwargs={'pk': workspace.id})
        response = client.put(url, data={'name': 'Updated Workspace'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_workspace_as_non_owner(self, user, team, workspace):
        non_owner = User.objects.create_user(email='nonowner@example.com', password='testpassword')

        client = APIClient()
        client.force_authenticate(user=non_owner)

        url = reverse('workspace:workspace-detail', kwargs={'pk': workspace.id})
        response = client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_workspace_as_owner(self, user, team):
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('workspace:workspace-list')
        response = client.post(url, data={'name': 'New Workspace'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Workspace'

    def test_update_workspace_as_owner(self, user, team, workspace):
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('workspace:workspace-detail', kwargs={'pk': workspace.id})
        response = client.put(url, data={'name': 'Updated Workspace'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Workspace'

    def test_delete_workspace_as_owner(self, user, team, workspace):
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('workspace:workspace-detail', kwargs={'pk': workspace.id})
        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_add_user_to_workspace_as_owner(self, user, team, workspace):
        new_user = User.objects.create_user(email='newuser@example.com', password='testpassword')
        role = 'SOCIAL_MEDIA_MANAGER'

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('workspace:workspace-user-add', kwargs={'pk': workspace.id})
        response = client.post(url, data={'user_id': new_user.id, 'role': role})
        assert response.status_code == status.HTTP_200_OK
        workspace_role = WorkspaceRole.objects.filter(workspace=workspace, user=new_user).first()
        assert workspace_role
        assert workspace_role.role == role

    def test_remove_user_from_workspace_as_owner(self, user, team, workspace):
        team_member = User.objects.create_user(email='member@example.com', password='testpassword')
        workspace_role = WorkspaceRole.objects.create(workspace=workspace, user=team_member, role='member')

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('workspace:workspace-user-remove', kwargs={'pk': workspace.id})
        response = client.post(url, data={'workspace_role_id': workspace_role.id})

        assert response.status_code == status.HTTP_200_OK
        assert team_member not in workspace.users.all()

    #TODO:
    # def test_list_social_media_accounts_authenticated_owner(self, user, team, workspace):
    #     instagram_account = InstagramAccount.objects.create(
    #         access_token="instagram_access_token",
    #         username="test_instagram",
    #         workspace=workspace,
    #     )
    #
    #     client = APIClient()
    #     client.force_authenticate(user=user)
    #
    #     url = reverse('workspace:workspace-list-social-media-accounts', kwargs={'pk': workspace.id})
    #     response = client.get(url)
    #
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.data) == 1
    #
    #     assert response.data[0]['username'] == 'test_instagram'
    #     assert response.data[0]['platform'] == SocialMediaPlatform.INSTAGRAM
    #
    # def test_list_social_media_accounts_authenticated_team_member(self, user, team, workspace):
    #     team_member = User.objects.create_user(email='member@example.com', password='testpassword')
    #     workspace.users.add(team_member)
    #
    #     instagram_account = InstagramAccount.objects.create(
    #         access_token="instagram_access_token",
    #         username="test_instagram",
    #         workspace=workspace,
    #     )
    #
    #     client = APIClient()
    #     client.force_authenticate(user=team_member)
    #
    #     url = reverse('workspace:workspace-list-social-media-accounts', kwargs={'pk': workspace.id})
    #     response = client.get(url)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.data) == 1
    #     assert response.data[0]['username'] == 'test_instagram'
    #     assert response.data[0]['platform'] == SocialMediaPlatform.INSTAGRAM
    #
    # def test_list_social_media_accounts_unauthenticated(self, user, team, workspace):
    #     instagram_account = InstagramAccount.objects.create(
    #         access_token="instagram_access_token",
    #         username="test_instagram",
    #         workspace=workspace,
    #     )
    #
    #     client = APIClient()
    #
    #     url = reverse('workspace:workspace-list-social-media-accounts', kwargs={'pk': workspace.id})
    #     response = client.get(url)
    #
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
    #
    # def test_list_social_media_accounts_non_member(self, user, team, workspace):
    #     non_member = User.objects.create_user(email='nonmember@example.com', password='testpassword')
    #
    #     instagram_account = InstagramAccount.objects.create(
    #         access_token="instagram_access_token",
    #         username="test_instagram",
    #         workspace=workspace,
    #     )
    #
    #     client = APIClient()
    #     client.force_authenticate(user=non_member)
    #
    #     url = reverse('workspace:workspace-list-social-media-accounts', kwargs={'pk': workspace.id})
    #     response = client.get(url)
    #
    #     assert response.status_code == status.HTTP_404_NOT_FOUND

    # def test_list_social_media_accounts_multiple_platforms(self, user, team, workspace):
    #     instagram_account = InstagramAccount.objects.create(
    #         access_token="instagram_access_token",
    #         username="test_instagram",
    #         workspace=workspace,
    #     )
    #
    #     twitter_account = SocialMediaAccount.objects.create(
    #         platform=SocialMediaPlatform.TWITTER,
    #         username="test_twitter",
    #         workspace=workspace,
    #     )
    #
    #     client = APIClient()
    #     client.force_authenticate(user=user)
    #
    #     url = reverse('workspace:workspace-list-social-media-accounts', kwargs={'pk': workspace.id})
    #     response = client.get(url)
    #
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.data) == 2
    #     assert any(
    #         account['username'] == 'test_instagram' and account['platform'] == SocialMediaPlatform.INSTAGRAM for account
    #         in response.data)
    #     assert any(
    #         account['username'] == 'test_twitter' and account['platform'] == SocialMediaPlatform.TWITTER for account in
    #         response.data)
