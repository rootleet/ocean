import hashlib
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.shortcuts import render, redirect

from admin_panel.models import Contacts
from taskmanager.forms import NewTask, NewTaskTransaction
from taskmanager.models import Tasks, TaskTransactions


@login_required()
def new_task(request):
    md_mix = f"{request.user.pk} {datetime.now()}"
    hash_object = hashlib.md5(md_mix.encode())
    uni = hash_object.hexdigest()
    contacts = Contacts.objects.filter(owner=request.user)
    context = {
        'nav': True,
        'contacts': contacts,
        'uni': uni
    }
    return render(request, 'taskmanager/new_task.html', context=context)


def save_new_task(request):
    if request.method == 'POST':
        form = NewTask(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Task Saved')
            except Exception as e:
                messages.error(request, f"Error Saving Task {e}")
        else:
            messages.error(request, "Could Not Save Task")

    else:
        messages.error(request, "Invalid Request Method")

    return redirect('my_tasks')


@login_required()
def my_tasks(request):
    me = User.objects.get(pk=request.user.pk)
    context = {
        'nav': True,
        'my_tasks': Tasks.objects.filter(owner=me,status=1).order_by('-pk')
    }
    return render(request, 'taskmanager/mytasks.html', context=context)


@login_required()
def task(request, url):
    taskx = Tasks.objects.get(uni=url)
    context = {
        'nav': True,
        'task': taskx
    }
    return render(request, 'taskmanager/task.html', context=context)


@login_required()
def update_task(request, url):
    context = {
        'nav': True,
        'task': Tasks.objects.get(uni=url).pk
    }
    return render(request, 'taskmanager/update.html', context=context)

@login_required()
def new_task_tran(request):
    if request.method == 'POST':
        form = NewTaskTransaction(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Transaction Saved')
                return redirect('task', form.cleaned_data['task'].uni)
            except Exception as e:
                messages.error(request, f"Error Saving Transaction {e}")
        else:

            messages.error(request, "Could Not Save Transaction")
    else:
        messages.error(request, "Invalid Request Method")

    return redirect(request.META.get('HTTP_REFERER'))


@login_required()
def close_task(request, uni):
    task = Tasks.objects.get(uni=uni)
    TaskTransactions(task=task, title='CLOSED', description="Task has been closed",
                     owner=User.objects.get(pk=request.user.pk)).save()
    task.status = 2
    task.save()

    messages.success(request, "Task Closed")
    return redirect('task', uni)
