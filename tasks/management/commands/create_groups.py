from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from tasks.models import Task
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Create user groups and assign permissions"

    def handle(self, *args, **options):
        # Definuj skupiny
        groups = {
            "Reader": ["view_task"],
            "Editor": ["view_task", "change_task"],
            "Manager": ["view_task", "change_task", "delete_task"],
            "Admin": ["view_task", "change_task", "delete_task", "add_task", "change_user", "delete_user", "add_user"]
        }

        content_type = ContentType.objects.get_for_model(Task)

        for group_name, perms in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for perm_codename in perms:
                try:
                    perm = Permission.objects.get(codename=perm_codename, content_type=content_type)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Permission {perm_codename} not found"))
            group.save()
            self.stdout.write(self.style.SUCCESS(f"Group {group_name} created/updated"))
