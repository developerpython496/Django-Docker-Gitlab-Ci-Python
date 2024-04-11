from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    SOCIAL_MEDIA_MANAGER = 'SOCIAL_MEDIA_MANAGER', _('Social Media Manager')
    CONTENT_CREATOR = 'CONTENT_CREATOR', _('Content Creator')
    ADS_MANAGER = 'ADS_MANAGER', _('Ads Manager')
    ANALYST = 'ANALYST', _('Analyst')


class Workspace(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField("core.User", through='WorkspaceRole', related_name='associated_workspaces')
    team = models.ForeignKey("core.Team", on_delete=models.CASCADE, related_name='workspaces')
    is_default = models.BooleanField(default=False, editable=False)  # Workspace that is created on registration.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            original = Workspace.objects.get(pk=self.pk)
            if original.team != self.team:
                raise ValidationError(_("Changing the owner of a workspace is not allowed."))
        super(Workspace, self).save(*args, **kwargs)


class WorkspaceRole(models.Model):
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.SOCIAL_MEDIA_MANAGER,
        verbose_name=_("User role in a workspace"),
        help_text=_("User role in a workspace"),
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='roles')
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('workspace', 'user')

    def __str__(self):
        return f'{self.user.email} - {self.role} - {self.workspace.name}'

    def save(self, *args, **kwargs):
        # Check if the user is the owner of the current team
        if hasattr(self.user, "owned_team") and self.user.owned_team == self.workspace.team:
            raise ValidationError(_("The user is the owner of this team and cannot be in another team's workspace."))

        # Check if the user is already in another team's workspace
        for workspace_role in self.user.roles.all():
            if workspace_role.workspace.team != self.workspace.team:
                raise ValidationError(_("The user is already in another team's workspace and cannot be added."))

        super(WorkspaceRole, self).save(*args, **kwargs)
