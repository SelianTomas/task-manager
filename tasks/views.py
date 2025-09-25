from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Task
from .forms import TaskForm


def register(request):
    """Registrácia nového používateľa"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Účet pre {user.username} bol úspešne vytvorený! Môžete sa prihlásiť.')
            return redirect("account_login")
        else:
            messages.error(request, 'Pri registrácii došlo k chybe. Skontrolujte zadané údaje.')
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
@permission_required('tasks.view_task', raise_exception=True)
def task_list(request):
    """Zoznam úloh s filtrovaním a vyhľadávaním"""
    tasks = Task.objects.all()

    # Vyhľadávanie
    search_query = request.GET.get('search')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filtrovanie podľa stavu
    status_filter = request.GET.get('status')
    if status_filter == 'completed':
        tasks = tasks.filter(completed=True)
    elif status_filter == 'pending':
        tasks = tasks.filter(completed=False)
    elif status_filter == 'overdue':
        today = timezone.now().date()
        tasks = tasks.filter(due_date__lt=today, completed=False)

    # Filtrovanie podľa termínu
    due_filter = request.GET.get('due')
    if due_filter == 'today':
        today = timezone.now().date()
        tasks = tasks.filter(due_date=today)
    elif due_filter == 'week':
        today = timezone.now().date()
        week_end = today + timedelta(days=7)
        tasks = tasks.filter(due_date__range=[today, week_end])

    # Zoradenie
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by in ['title', 'due_date', 'created_at', 'completed']:
        if request.GET.get('order') == 'asc':
            tasks = tasks.order_by(sort_by)
        else:
            tasks = tasks.order_by(f'-{sort_by}')
    else:
        tasks = tasks.order_by('-created_at')

    # Stránkovanie
    paginator = Paginator(tasks, 10)  # 10 úloh na stránku
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Štatistiky
    all_tasks = Task.objects.all()
    stats = {
        'total': all_tasks.count(),
        'completed': all_tasks.filter(completed=True).count(),
        'pending': all_tasks.filter(completed=False).count(),
        'overdue': all_tasks.filter(
            due_date__lt=timezone.now().date(),
            completed=False
        ).count() if all_tasks.exists() else 0,
    }

    context = {
        'page_obj': page_obj,
        'tasks': page_obj.object_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'due_filter': due_filter,
        'sort_by': sort_by,
        'stats': stats,
    }

    return render(request, 'tasks/task_list.html', context)


@login_required
@permission_required('tasks.add_task', raise_exception=True)
def task_create(request):
    """Vytvorenie novej úlohy"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Úloha "{task.title}" bola úspešne vytvorená!')
            return redirect('task_list')
        else:
            messages.error(request, 'Pri vytváraní úlohy došlo k chybe. Skontrolujte zadané údaje.')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'action': 'create'
    })


@login_required
@permission_required('tasks.change_task', raise_exception=True)
def task_update(request, pk):
    """Úprava existujúcej úlohy"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()
            messages.success(request, f'Úloha "{updated_task.title}" bola úspešne aktualizovaná!')
            return redirect('task_list')
        else:
            messages.error(request, 'Pri aktualizácii úlohy došlo k chybe. Skontrolujte zadané údaje.')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'action': 'update'
    })

@login_required
@permission_required('tasks.delete_task', raise_exception=True)
def task_delete(request, pk):
    """Zmazanie úlohy"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Úloha "{task_title}" bola úspešne zmazaná!')
        return redirect('task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
@permission_required('tasks.change_task', raise_exception=True)
def task_toggle_status(request, pk):
    """Rápide prepnutie stavu úlohy (AJAX endpoint)"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        task.completed = not task.completed
        task.save()

        status = "dokončená" if task.completed else "označená ako nedokončená"
        messages.success(request, f'Úloha "{task.title}" bola {status}!')

        # Pre AJAX požiadavky vrátime JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'status': 'success',
                'completed': task.completed,
                'message': f'Úloha bola {status}!'
            })

    return redirect('task_list')

@login_required
def dashboard(request):
    """Dashboard s prehľadom úloh"""
    if not request.user.has_perm('tasks.view_task'):
        messages.error(request, 'Nemáte oprávnenie na zobrazenie dashboardu.')
        return redirect('account_login')

    today = timezone.now().date()

    # Získanie relevantných úloh
    all_tasks = Task.objects.all()
    today_tasks = all_tasks.filter(due_date=today)
    upcoming_tasks = all_tasks.filter(
        due_date__gt=today,
        due_date__lte=today + timedelta(days=7),
        completed=False
    )
    overdue_tasks = all_tasks.filter(
        due_date__lt=today,
        completed=False
    )
    recent_completed = all_tasks.filter(
        completed=True
    ).order_by('-created_at')[:5]

    # Štatistiky
    stats = {
        'total': all_tasks.count(),
        'completed': all_tasks.filter(completed=True).count(),
        'pending': all_tasks.filter(completed=False).count(),
        'overdue': overdue_tasks.count(),
        'today': today_tasks.count(),
        'upcoming': upcoming_tasks.count(),
    }

    context = {
        'stats': stats,
        'today_tasks': today_tasks,
        'upcoming_tasks': upcoming_tasks[:5],  # Len prvých 5
        'overdue_tasks': overdue_tasks[:5],    # Len prvých 5
        'recent_completed': recent_completed,
        'today_date': today,
    }

    return render(request, 'tasks/dashboard.html', context)

# API endpoint pre získanie štatistík (pre budúce AJAX použitie)
@login_required
@permission_required('tasks.view_task', raise_exception=True)
def task_stats_api(request):
    """API endpoint pre štatistiky úloh"""
    from django.http import JsonResponse

    all_tasks = Task.objects.all()
    today = timezone.now().date()

    stats = {
        'total': all_tasks.count(),
        'completed': all_tasks.filter(completed=True).count(),
        'pending': all_tasks.filter(completed=False).count(),
        'overdue': all_tasks.filter(
            due_date__lt=today,
            completed=False
        ).count(),
        'due_today': all_tasks.filter(due_date=today).count(),
        'due_this_week': all_tasks.filter(
            due_date__range=[today, today + timedelta(days=7)]
        ).count(),
    }

    return JsonResponse(stats)