from typing import Tuple, Optional, List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.models import Team
from workspace.models import Workspace, WorkspaceRole, Role
from social_media.models import SocialMediaAccount, InstagramAccount

User = get_user_model()




class WorkspaceService:

    @staticmethod
    def can_create_workspace(team_id: int) -> bool:
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return False

        owned_workspaces_count = Workspace.objects.filter(team=team).count()
        return owned_workspaces_count < team.owner.stripe_user.max_workspaces

    @staticmethod
    def create_workspace(team_id: int, name: str) -> Tuple[bool, Optional[Workspace], str]:
        can_create = WorkspaceService.can_create_workspace(team_id=team_id)
        if not can_create:
            return False, None, _("User is not allowed to create new workspace.")
        if not name:
            return False, None, _("Workspace name cannot be empty.")

        workspace = Workspace.objects.create(team_id=team_id, name=name)
        return True, workspace, _("Workspace created successfully.")

    @staticmethod
    def update_workspace_name(workspace_id: int, new_name: str) -> Tuple[bool, Optional[Workspace], str]:
        workspace = Workspace.objects.filter(pk=workspace_id).first()
        if not workspace:
            return False, None, _("Workspace not found.")
        if not new_name:
            return False, None, _("Workspace name cannot be empty.")

        workspace.name = new_name
        workspace.save()
        return True, workspace, _("Workspace name updated successfully.")

    @staticmethod
    def delete_workspace(workspace_id: int) -> Tuple[bool, str]:
        workspace = Workspace.objects.filter(pk=workspace_id).first()
        if not workspace:
            return False, _("Workspace not found.")
        if workspace.is_default:
            return False, _("Cannot delete the initial workspace.")
        workspace.delete()
        return True, _("Workspace deleted successfully.")

    @staticmethod
    def get_users_in_workspace(workspace_id: int) -> List[User]:
        workspace = Workspace.objects.filter(pk=workspace_id)
        if workspace.exists():
            return workspace.first().users.all()
        return []

    @staticmethod
    def add_user_to_workspace(workspace_id: int, user_id: int, role: str) -> Tuple[bool, Optional[WorkspaceRole], str]:
        valid_roles = [role for role, x in Role.choices]
        if role not in valid_roles:
            return False, None, _("Invalid role.")

        workspace = Workspace.objects.filter(pk=workspace_id).first()
        if not workspace:
            return False, None, _("Workspace not found.")

        owner_id = workspace.team.owner_id
        if not WorkspaceService.can_add_user_to_owned_workspaces(owner_id):
            return False, None, _("Cannot add more users to workspaces owned by this user.")

        user = User.objects.filter(pk=user_id).first()
        if not user:
            return False, None, _("User not found.")

        workspace_role = WorkspaceRole.objects.create(workspace=workspace, user=user, role=role)
        return True, workspace_role, _("User added to workspace successfully.")

    @staticmethod
    def remove_user_from_workspace(workspace_role_id: int) -> Tuple[bool, str]:
        workspace_role = WorkspaceRole.objects.filter(pk=workspace_role_id)
        if not workspace_role.exists():
            return False, _("Workspace role not found.")

        workspace_role.delete()
        return True, _("User removed from workspace successfully.")

    @staticmethod
    def update_user_role_in_workspace(workspace_role_id: int, role: str) -> Tuple[bool, Optional[WorkspaceRole], str]:
        valid_roles = [role for role, x in Role.choices]
        if role not in valid_roles:
            return False, None, _("Invalid role.")

        workspace_role = WorkspaceRole.objects.filter(pk=workspace_role_id).first()
        if not workspace_role:
            return False, None, _("Workspace role not found.")

        workspace_role.role = role
        workspace_role.save()
        return True, workspace_role, _("User role updated successfully.")

    @staticmethod
    def can_add_user_to_owned_workspaces(owner_id: int) -> bool:
        owner = User.objects.filter(id=owner_id).first()
        if not owner:
            return False

        workspaces = Workspace.objects.filter(team__owner=owner)
        unique_users = {user for workspace in workspaces for user in workspace.users.all()}
        total_users = len(unique_users)

        return total_users < owner.stripe_user.max_users

    @staticmethod
    def get_social_media_accounts_in_workspace(workspace_id: int) -> List[SocialMediaAccount]:
        workspace = Workspace.objects.filter(pk=workspace_id)
        if workspace.exists():
            workspace = workspace.first()
            return workspace.social_media_accounts.all()
        return InstagramAccount.objects.none()

    @staticmethod
    def can_add_social_media_account_to_owner_workspaces(owner_id: int) -> Tuple[bool, int]:
        owner = User.objects.filter(pk=owner_id)
        if not owner or not owner.subscription:
            return False, 0

        workspaces = Workspace.objects.filter(team__owner_id=owner_id)
        total_social_media_accounts = 0
        for workspace in workspaces:
            total_social_media_accounts += workspace.social_media_accounts.count()
        return total_social_media_accounts < owner.stripe_user.max_socials, total_social_media_accounts

    @staticmethod
    def add_social_media_account_to_workspace(workspace_id: int, account_id: int) -> \
            Tuple[bool, Optional[SocialMediaAccount], str]:
        if not Workspace.objects.filter(pk=workspace_id).exists():
            return False, None, _("Workspace not found.")

        workspace = Workspace.objects.get(pk=workspace_id)

        can_add, x = WorkspaceService.can_add_social_media_account_to_owner_workspaces(workspace.team.owner_id)
        if not can_add:
            return False, None, _("Cannot add more social media accounts to this owner's workspaces.")

        account = SocialMediaAccount.objects.filter(pk=account_id)
        if not account.exists():
            return False, None, _("Social media account not found.")

        account.workspace = workspace
        account.save()
        return True, account, _("Social media account added to workspace successfully.")

    @staticmethod
    def remove_social_media_account_from_workspace(workspace_id: int, account_id: int) -> \
            Tuple[bool, Optional[SocialMediaAccount], str]:
        if not Workspace.objects.filter(pk=workspace_id).exists():
            return False, None, _("Workspace not found.")

        workspace = Workspace.objects.get(pk=workspace_id)

        if not workspace.social_media_accounts.filter(pk=account_id).exists():
            return False, None, _("Social media account not found.")

        account = workspace.social_media_accounts.get(pk=account_id)
        account.workspace = None
        account.save()
        return True, account, _("Social media account removed from workspace successfully.")
