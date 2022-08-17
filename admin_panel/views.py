from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from community.models import *
from admin_panel.models import *
from blog.models import *


def index(request):
    return render(request, 'index.html')


def all_issues(request):
    issues = questions.objects.all()
    context = {
        'issues': issues
    }
    return render(request, 'all_issues.html', context=context)


def view_issue(request, issue_id):
    issue = questions.objects.get(uni=issue_id)
    context = {
        'issue': issue
    }
    return render(request, 'view_issue.html', context=context)


def log_issue(request):
    if request.method == 'GET':
        current_user = request.user
        user_id = current_user.id
        form = request.GET
        title = form['title']
        body = form['body']
        issue = form['issue']

        log = LoggedIssue(issue=issue)
        log_tran = LoggedIssueTransaction(issue=issue, title=title, body=body, created_by=user_id)
        ans = answers(user=user_id, question=issue, ans='Issue logged by admin')
        notification = Notofication(sent_from=user_id,sent_to=user_id,title='Issue Logged',message='Your issue has '
                                                                                                   'been logged ('
                                                                                                   '12345). track '
                                                                                                   'issue with issue '
                                                                                                   'tracker')

        try:
            log.save()
            log_tran.save()
            ans.save()
            notification.save()
            return HttpResponse(f'done%%{issue} logged')
        except Exception as e:
            return HttpResponse(f'error%%Flied Logging Issue {e}')




    else:
        return HttpResponse('WRONG')


def all_task(request):
    tasks = LoggedIssue.objects.all()
    context = {
        'tasks': tasks
    }
    return render(request, 'all_task.html', context=context)