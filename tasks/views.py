# tasks/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from .models import Task
from .forms import TaskForm


def user_can_see_all_tasks(user):
    """Kontrola či používateľ môže vidieť všetky tasky"""
    return (user.is_superuser or
            user.groups.filter(name__in=['Admin', 'Manager', 'Editor', 'Reader']).exists())


def user_can_edit_tasks(user):
    """Kontrola či používateľ môže upravovať tasky"""
    return (user.is_superuser or
            user.groups.filter(name__in=['Admin', 'Manager', 'Editor']).exists())


def user_can_delete_tasks(user):
    """Kontrola či používateľ môže mazať tasky"""
    return (user.is_superuser or
            user.groups.filter(name__in=['Admin', 'Manager']).exists())


@login_required
def task_list(request):
    """Zoznam úloh podľa oprávnení používateľa"""
    # Získanie všetkých taskov podľa oprávnení
    if user_can_see_all_tasks(request.user):
        all_tasks = Task.objects.all()
        can_see_all = True
    else:
        all_tasks = Task.objects.filter(user=request.user)
        can_see_all = False

    # Filtrovanie podľa GET parametra
    filter_by = request.GET.get('filter', 'all')
    today = timezone.now().date()

    if filter_by == 'completed':
        tasks = all_tasks.filter(completed=True)
    elif filter_by == 'pending':
        tasks = all_tasks.filter(completed=False)
    elif filter_by == 'overdue':
        tasks = all_tasks.filter(completed=False, due_date__lt=today)
    else:
        tasks = all_tasks

    tasks = tasks.order_by("-created_at")

    # Štatistiky
    stats = {
        'total': all_tasks.count(),
        'completed': all_tasks.filter(completed=True).count(),
        'pending': all_tasks.filter(completed=False).count(),
        'overdue': all_tasks.filter(completed=False, due_date__lt=today).count(),
    }

    context = {
        'tasks': tasks,
        'stats': stats,
        'current_filter': filter_by,
        'can_see_all_tasks': can_see_all,
        'can_edit_tasks': user_can_edit_tasks(request.user),
        'can_delete_tasks': user_can_delete_tasks(request.user),
        'user_groups': [group.name for group in request.user.groups.all()],
    }
    return render(request, "tasks/task_list.html", context)


# Ostatné views zostávajú rovnaké...
@login_required
@permission_required('tasks.add_task', raise_exception=True)
def task_create(request):
    """Vytvorenie novej úlohy"""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Úloha "{task.title}" bola úspešne vytvorená!')
            return redirect("task_list")
        else:
            messages.error(request, 'Chyba pri vytváraní úlohy. Skontrolujte zadané údaje.')
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form})


@login_required
def task_edit(request, pk):
    """Úprava existujúcej úlohy"""
    if user_can_see_all_tasks(request.user):
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, user=request.user)

    if not user_can_edit_tasks(request.user) and task.user != request.user:
        messages.error(request, 'Nemáte oprávnenie upravovať túto úlohu.')
        return redirect('task_list')

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Úloha "{task.title}" bola aktualizovaná!')
            return redirect("task_list")
        else:
            messages.error(request, 'Chyba pri aktualizácii úlohy.')
    else:
        form = TaskForm(instance=task)

    return render(request, "tasks/task_form.html", {"form": form, "task": task})


@login_required
@require_POST
def task_delete(request, pk):
    """Zmazanie úlohy"""
    if user_can_see_all_tasks(request.user):
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, user=request.user)

    if not user_can_delete_tasks(request.user) and task.user != request.user:
        messages.error(request, 'Nemáte oprávnenie zmazať túto úlohu.')
        return redirect('task_list')

    task_title = task.title
    task.delete()
    messages.success(request, f'Úloha "{task_title}" bola zmazaná!')
    return redirect("task_list")


@login_required
@require_POST
def task_toggle_complete(request, pk):
    """Prepnutie stavu dokončenia úlohy"""
    if user_can_see_all_tasks(request.user):
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, user=request.user)

    if not user_can_edit_tasks(request.user) and task.user != request.user:
        messages.error(request, 'Nemáte oprávnenie upravovať túto úlohu.')
        return redirect('task_list')

    with transaction.atomic():
        task.completed = not task.completed
        task.save()

    status = "dokončená" if task.completed else "nedokončená"
    messages.success(request, f'Úloha "{task.title}" je teraz {status}!')
    return redirect("task_list")