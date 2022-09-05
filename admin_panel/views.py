from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests
import hashlib

# Create your views here.
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from community.models import *
from admin_panel.models import *
from blog.models import *
from ocean import settings


def index(request):
    current_user = request.user
    if current_user.is_active:
        return render(request, 'index.html')
    else:
        return redirect('login')


def all_issues(request):
    issues = questions.objects.all()
    context = {
        'page-title': 'ALL ISSUES',
        'issues': issues
    }
    return render(request, 'all_issues.html', context=context)


def view_issue(request, issue_id):
    issue = questions.objects.get(uni=issue_id)
    task_count = TaskHD.object.filter(ref=issue_id).count()
    context = {
        'issue': issue,
        'task_count':task_count
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
        notification = Notofication(sent_from=user_id, sent_to=user_id, title='Issue Logged', message='Your issue has '
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
    prov = Providers.objects.all()
    context = {
        'tasks': tasks, 'providers': prov
    }
    return render(request, 'all_task.html', context=context)


def mark_esc(request):
    if request.method == 'GET':
        current_user = request.user
        user_id = current_user.id
        form = request.GET
        issue = form['issue']


        # MARK ISSIE
        # get question details
        target_question = questions.objects.get(uni=issue)
        tag = target_question.domain



        tag_details = tags.objects.get(tag_code=tag).provider
        return HttpResponse(f"{tag}")

        provider_details = Providers.objects.get(pk=tag_details).provider_code
        try:
            PendingEscalations(provider=provider_details, issue=issue).save()
            return HttpResponse("done%% Issue Marked")
        except Exception as e:
            return HttpResponse(f"error%%{e} {provider_details}")


def to_scalate(request):
    x_counts = PendingEscalations.objects.all().values('provider').annotate(total=Count('provider')).order_by('total')
    context = {
        'x_count': x_counts
    }
    return render(request, 'to_escalate.html', context=context)


def escalate_detail(request, provider):
    prov_det = Providers.objects.get(provider_code=provider)
    issues = PendingEscalations.objects.filter(provider=provider)
    context = {
        'provider': prov_det,
        'questions': issues
    }
    return render(request, 'escalate_detail.html', context=context)


def send_to_provider(request):
    if request.method == 'GET':
        current_user = request.user
        user_id = current_user.id
        form = request.GET

        c_provider = form['x_provider']

        prov_det = Providers.objects.get(provider_code=c_provider)
        issues = PendingEscalations.objects.filter(provider=c_provider)
        # get all logs
        email_text = form['email']
        recipient_list = [prov_det.email]
        subject = form['subject']
        send_mail(subject, email_text, 'robolog', recipient_list, html_message=email_text,
                  fail_silently=False)

        return HttpResponse(f"done%%Issue Sent To {c_provider}")


def accessories(request):
    all_tags = tags.objects.all()
    context = {
        'tags': all_tags,
        'providers': Providers.objects.all()
    }
    return render(request, 'accessories.html', context=context)


def new_provider(request):
    if request.method == 'POST':
        form = request.POST
        code = form['code']
        description = form['description']
        mobile = form['mobile']
        email = form['email']

        if Providers.objects.filter(provider_code=code).count() < 1:
            # save
            save_provider = Providers(provider_code=code, descr=description, mobile=mobile, email=email)
            save_provider.save()
            return redirect('accessories')


def new_tag(request):
    if request.method == 'POST':
        form = request.POST
        code = form['code']
        description = form['description']
        provider = form['provider']

        if tags.objects.filter(tag_code=code).count() < 1:
            # save
            save = tags(tag_code=code, tag_dec=description, provider=provider)
            save.save()
            return redirect('accessories')
        else:
            return HttpResponse(f"{code} EXIST")


def add_to_task(request):
    if request.method == 'POST':
        form = request.POST
        user = request.user

        owner = form['owner']
        title = form['title']
        description = form['description']
        tried = form['tried']
        ref = form['question']

        md_mix = f"{title} {owner} {description} {tried}{user.pk}{user.username}"
        hash_object = hashlib.md5(md_mix.encode())
        md5_hash = hash_object.hexdigest()

        comment = answers(user=user.pk,question=ref,ans="I have logged a task from your issue and it will be resolved soon")
        task_hd = TaskHD(entry_uni=ref, type='from_questions', ref=ref, owner=user.pk, title=title,description=description)

        try:
            task_hd.save()
            comment.save()
            return HttpResponse(f'done%%')
        except Exception as e :
            return HttpResponse(f'error%%{e}')