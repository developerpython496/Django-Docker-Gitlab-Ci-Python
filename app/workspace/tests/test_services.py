import pytest
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.models import Team
from workspace.models import Workspace
from workspace.services import WorkspaceService
from social_media.models import InstagramAccount
from subscription.models import Subscription, StripeUser, Feature, Product, ProductFeature, Price, SubscriptionItem

User = get_user_model()


@pytest.fixture
def create_team_with_users():
    def _create_team_with_users(num_users):
        owner = User.objects.create_user(
            email='testowner@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Owner'
        )
        stripe_user = StripeUser.objects.create(user=owner)
        team = Team.objects.create(name='Test Team', owner=owner)
        for i in range(num_users):
            user = User.objects.create_user(
                email=f'testuser{i}@example.com',
                password='testpassword',
                first_name=f'Test{i}',
                last_name='User'
            )
            workspace = Workspace.objects.create(name=f'Test Workspace {i}', team=team)
            workspace.users.add(user)
        return team

    return _create_team_with_users


@pytest.fixture
def create_team_with_users_and_subscription():
    def _create_team_with_users_and_subscription(num_users):
        owner = User.objects.create_user(
            email='testowner@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Owner'
        )

        stripe_user = StripeUser.objects.create(user=owner)

        max_workspaces_feature = Feature.objects.create(feature_id=f'max_workspaces__3')
        max_users_feature = Feature.objects.create(feature_id=f'max_users__3')
        max_socials_feature = Feature.objects.create(feature_id=f'max_socials__3')
        product = Product.objects.create(product_id='product_test', active=True)
        ProductFeature.objects.create(product=product, feature=max_workspaces_feature)
        ProductFeature.objects.create(product=product, feature=max_users_feature)
        ProductFeature.objects.create(product=product, feature=max_socials_feature)
        price = Price.objects.create(price_id='price_test', product=product, price=999, active=True, currency='USD')
        subscription = Subscription.objects.create(stripe_user=stripe_user, status='active', cancel_at_period_end=False)
        SubscriptionItem.objects.create(subscription=subscription, price=price, quantity=1)

        team = Team.objects.create(name='Test Team', owner=owner)
        team.owner = owner
        for i in range(num_users):
            user = User.objects.create_user(
                email=f'testuser{i}@example.com',
                password='testpassword',
                first_name=f'Test{i}',
                last_name='User'
            )
            workspace = Workspace.objects.create(name=f'Test Workspace {i}', team=team)
            workspace.users.add(user)
        return team

    return _create_team_with_users_and_subscription


@pytest.mark.django_db
class TestWorkspaceService:
    def test_can_create_workspace_with_existing_team_and_quota_available(self, create_team_with_users_and_subscription):
        team = create_team_with_users_and_subscription(num_users=1)

        result = WorkspaceService.can_create_workspace(team_id=team.id)

        assert result

    def test_can_create_workspace_with_nonexistent_team(self):
        team_id = 1

        result = WorkspaceService.can_create_workspace(team_id=team_id)

        assert not result

    def test_create_workspace_with_existing_team_and_quota_available(self, create_team_with_users_and_subscription):
        team = create_team_with_users_and_subscription(num_users=1)

        result = WorkspaceService.create_workspace(team_id=team.id, name='New Workspace')

        assert result[0]
        assert result[1]
        assert result[2] == _("Workspace created successfully.")
        assert team.workspaces.filter(name='New Workspace').exists()

    def test_create_workspace_with_existing_team_and_quota_exceeded(self, create_team_with_users_and_subscription):
        team = create_team_with_users_and_subscription(num_users=3)

        result = WorkspaceService.create_workspace(team_id=team.id, name='New Workspace')

        assert not result[0]
        assert not result[1]
        assert result[2] == _("User is not allowed to create new workspace.")
        assert not team.workspaces.filter(name='New Workspace').exists()

    def test_create_workspace_with_nonexistent_team(self):
        team_id = 1

        result = WorkspaceService.create_workspace(team_id=team_id, name='New Workspace')

        assert not result[0]
        assert not result[1]
        assert result[2] == _("User is not allowed to create new workspace.")
        assert not Workspace.objects.filter(name='New Workspace').exists()

    def test_create_workspace_with_empty_name(self, create_team_with_users_and_subscription):
        team = create_team_with_users_and_subscription(num_users=1)
        max_workspaces_feature = Feature.objects.create(feature_id=f'max_workspaces__10')
        product = team.owner.stripe_user.current_subscription_items.first().price.product
        ProductFeature.objects.create(product=product, feature=max_workspaces_feature)

        result = WorkspaceService.create_workspace(team_id=team.id, name='')

        assert not result[0]
        assert not result[1]
        assert result[2] == _("Workspace name cannot be empty.")
        assert not team.workspaces.filter(name='').exists()

    def test_update_workspace_name_with_existing_workspace(self, create_team_with_users):
        team = create_team_with_users(num_users=1)
        workspace = team.workspaces.first()
        new_name = "Updated Workspace Name"

        result = WorkspaceService.update_workspace_name(workspace_id=workspace.id, new_name=new_name)

        assert result[0]
        assert result[1].name == new_name
        assert result[2] == _("Workspace name updated successfully.")

    def test_update_workspace_name_with_nonexistent_workspace(self):
        workspace_id = 1
        new_name = "Updated Workspace Name"

        result = WorkspaceService.update_workspace_name(workspace_id=workspace_id, new_name=new_name)

        assert not result[0]
        assert not result[1]
        assert result[2] == _("Workspace not found.")

    def test_update_workspace_name_with_empty_name(self, create_team_with_users):
        team = create_team_with_users(num_users=1)
        workspace = team.workspaces.first()

        result = WorkspaceService.update_workspace_name(workspace_id=workspace.id, new_name="")

        assert not result[0]
        assert not result[1]
        assert result[2] == _("Workspace name cannot be empty.")

    def test_delete_workspace_with_existing_workspace(self, create_team_with_users):
        team = create_team_with_users(num_users=1)
        workspace = team.workspaces.create(name="Workspace to be deleted")

        result = WorkspaceService.delete_workspace(workspace_id=workspace.id)

        assert result[0]
        assert result[1] == _("Workspace deleted successfully.")
        assert not team.workspaces.filter(name="Workspace to be deleted").exists()

    def test_delete_workspace_with_nonexistent_workspace(self):
        workspace_id = 1

        result = WorkspaceService.delete_workspace(workspace_id=workspace_id)

        assert not result[0]
        assert result[1] == _("Workspace not found.")

    def test_delete_workspace_with_default_workspace(self, create_team_with_users):
        team = create_team_with_users(num_users=1)
        default_workspace = Workspace.objects.create(team=team, is_default=True, )

        result = WorkspaceService.delete_workspace(workspace_id=default_workspace.id)
        assert not result[0]
        assert result[1] == _("Cannot delete the initial workspace.")

    def test_get_users_in_workspace_with_nonexistent_workspace(self):
        workspace_id = 1

        result = WorkspaceService.get_users_in_workspace(workspace_id=workspace_id)

        assert result == []

    def test_can_add_user_to_owned_workspaces_with_quota_available(self, create_team_with_users_and_subscription):
        team = create_team_with_users_and_subscription(num_users=1)

        result = WorkspaceService.can_add_user_to_owned_workspaces(owner_id=team.owner.id)

        assert result

    def test_can_add_user_to_owned_workspaces_with_quota_exceeded(self, create_team_with_users_and_subscription):
        team = create_team_with_users_and_subscription(num_users=3)

        result = WorkspaceService.can_add_user_to_owned_workspaces(owner_id=team.owner.id)

        assert not result

    def test_can_add_user_to_owned_workspaces_with_nonexistent_owner(self):
        owner_id = 1

        result = WorkspaceService.can_add_user_to_owned_workspaces(owner_id=owner_id)

        assert not result

    def test_can_add_user_to_owned_workspaces_with_no_subscription(self, create_team_with_users):
        team = create_team_with_users(num_users=1)
        owner = team.owner

        result = WorkspaceService.can_add_user_to_owned_workspaces(owner_id=owner.id)

        assert not result

    def test_can_add_user_to_owned_workspaces_same_user_in_two_workspaces(self,
                                                                          create_team_with_users_and_subscription):
        team = create_team_with_users_and_subscription(num_users=1)
        owner = team.owner
        workspace1 = team.workspaces.first()
        workspace2 = Workspace.objects.create(name='Test Workspace 2', team=team)
        other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpassword',
            first_name='Other',
            last_name='User'
        )

        workspace1.users.add(other_user)
        workspace2.users.add(other_user)

        result = WorkspaceService.can_add_user_to_owned_workspaces(owner_id=owner.id)

        assert result

    def test_get_social_media_accounts_in_workspace_with_existing_workspace(self, create_team_with_users):
        team = create_team_with_users(num_users=1)
        workspace = team.workspaces.first()
        social_media_account1 = InstagramAccount.objects.create(username="Social Media Account 1",
                                                                workspace=workspace,
                                                                access_token="a")
        social_media_account2 = InstagramAccount.objects.create(username="Social Media Account 2",
                                                                workspace=workspace,
                                                                access_token="b")

        result = WorkspaceService.get_social_media_accounts_in_workspace(workspace_id=workspace.id)

        assert len(result) == 2
        assert social_media_account1 in result
        assert social_media_account2 in result

    def test_get_social_media_accounts_in_workspace_with_non_existing_workspace(self):
        result = WorkspaceService.get_social_media_accounts_in_workspace(workspace_id=999)
        assert len(result) == 0

    # def test_can_add_social_media_account_to_owner_workspaces_success(self, create_team_with_users):
    #     team = create_team_with_users(num_users=1)
    #     owner = team.owner
    #     owner.subscription.max_socials = 3
    #     owner.subscription.save()
    #     workspace = team.workspaces.first()
    #     InstagramAccount.objects.create(username="Social Media Account 1", workspace=workspace, access_token="a")
    #
    #     can_add, total_social_media_accounts = WorkspaceService.can_add_social_media_account_to_owner_workspaces(
    #         owner_id=owner.id
    #     )
    #
    #     assert can_add
    #     assert total_social_media_accounts == 1
    #
    # def test_can_add_social_media_account_to_owner_workspaces_failure(self, create_team_with_users):
    #     team = create_team_with_users(num_users=1)
    #     owner = team.owner
    #     owner.subscription.max_socials = 1
    #     owner.subscription.save()
    #     workspace = team.workspaces.first()
    #     InstagramAccount.objects.create(username="Social Media Account 1", workspace=workspace, access_token="a")
    #
    #     can_add, total_social_media_accounts = WorkspaceService.can_add_social_media_account_to_owner_workspaces(
    #         owner_id=owner.id
    #     )
    #
    #     assert not can_add
    #     assert total_social_media_accounts == 1
    #
    # def test_add_social_media_account_to_workspace_success(self, create_team_with_users):
    #     team = create_team_with_users(num_users=1)
    #     owner = team.owner
    #     owner.subscription.max_socials = 2
    #     owner.subscription.save()
    #     workspace = team.workspaces.first()
    #     InstagramAccount.objects.create(username="Social Media Account 1", workspace=workspace, access_token="a")
    #     account = InstagramAccount.objects.create(username="Social Media Account 2", access_token="b")
    #
    #     success, added_account, message = WorkspaceService.add_social_media_account_to_workspace(
    #         workspace_id=workspace.id, account_id=account.id
    #     )
    #
    #     assert success
    #     assert added_account == account
    #     assert message == _("Social media account added to workspace successfully.")
    #
    # def test_add_social_media_account_to_workspace_failure_workspace_not_found(self):
    #     success, added_account, message = WorkspaceService.add_social_media_account_to_workspace(
    #         workspace_id=999, account_id=1
    #     )
    #
    #     assert not success
    #     assert added_account is None
    #     assert message == _("Workspace not found.")
    #
    # def test_add_social_media_account_to_workspace_failure_account_not_found(self, create_team_with_users):
    #     team = create_team_with_users(num_users=1)
    #     workspace = team.workspaces.first()
    #
    #     success, added_account, message = WorkspaceService.add_social_media_account_to_workspace(
    #         workspace_id=workspace.id, account_id=999
    #     )
    #
    #     assert not success
    #     assert added_account is None
    #     assert message == _("Social media account not found.")
    #
    # def test_remove_social_media_account_from_workspace_success(self, create_team_with_users):
    #     team = create_team_with_users(num_users=1)
    #     workspace = team.workspaces.first()
    #     account = InstagramAccount.objects.create(username="Social Media Account 1", workspace=workspace,
    #                                               access_token="a")
    #
    #     success, removed_account, message = WorkspaceService.remove_social_media_account_from_workspace(
    #         workspace_id=workspace.id, account_id=account.id
    #     )
    #
    #     assert success
    #     assert removed_account == account
    #     assert message == _("Social media account removed from workspace successfully.")
    #
    # def test_remove_social_media_account_from_workspace_failure_workspace_not_found(self, create_team_with_users):
    #     team = create_team_with_users(num_users=1)
    #     workspace = team.workspaces.first()
    #     account = InstagramAccount.objects.create(username="Social Media Account 1", workspace=workspace,
    #                                               access_token="a")
    #
    #     success, removed_account, message = WorkspaceService.remove_social_media_account_from_workspace(
    #         workspace_id=999, account_id=account.id
    #     )
    #
    #     assert not success
    #     assert removed_account is None
    #     assert message == _("Workspace not found.")
    #
    # def test_remove_social_media_account_from_workspace_failure_account_not_found(self, create_team_with_users):
    #     team = create_team_with_users(num_users=1)
    #     workspace = team.workspaces.first()
    #
    #     success, removed_account, message = WorkspaceService.remove_social_media_account_from_workspace(
    #         workspace_id=workspace.id, account_id=999
    #     )
    #
    #     assert not success
    #     assert removed_account is None
    #     assert message == _("Social media account not found.")
