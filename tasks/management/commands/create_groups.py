from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from tasks.models import Task
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Create user groups and assign permissions"

    def handle(self, *args, **options):
        # Získanie content types
        task_content_type = ContentType.objects.get_for_model(Task)

        # Definuj skupiny s oprávneniami
        groups = {
            "Reader": ["view_task", "add_task"],  # Čítať + vytvárať tasky
            "Editor": ["view_task", "add_task", "change_task"],  # Reader + upravovať
            "Manager": ["view_task", "add_task", "change_task", "delete_task"],  # Editor + mazať
            "Admin": ["view_task", "add_task", "change_task", "delete_task"]  # Všetko pre tasky
        }

        for group_name, perms in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)

            # Vymazanie starých oprávnení
            group.permissions.clear()

            # Pridanie nových oprávnení
            permissions_added = []
            for perm_codename in perms:
                try:
                    # Hľadáme oprávnenie pre Task model
                    perm = Permission.objects.get(
                        codename=perm_codename,
                        content_type=task_content_type
                    )
                    group.permissions.add(perm)
                    permissions_added.append(perm_codename)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Permission '{perm_codename}' not found for Task model"
                        )
                    )

            action = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Group '{group_name}' {action} with permissions: {', '.join(permissions_added)}"
                )
            )

        # Výpis súhrnu
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('📋 SÚHRN SKUPÍN A OPRÁVNENÍ:'))
        self.stdout.write('=' * 50)
        self.stdout.write('👀 Reader:  Zobraziť tasky + Vytvoriť tasky')
        self.stdout.write('✏️  Editor:  Reader + Upraviť tasky')
        self.stdout.write('🔧 Manager: Editor + Zmazať tasky')
        self.stdout.write('👑 Admin:   Všetky oprávnenia')
        self.stdout.write('=' * 50)

        self.stdout.write(self.style.SUCCESS('\n🎉 Všetky skupiny boli úspešne nastavené!'))