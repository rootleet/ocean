import os
from pathlib import Path

#from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests
import hashlib
import babel.numbers

# Create your views here.
from django.core import serializers
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
#from unicodecsv import writer
import datetime

from community.models import *
from admin_panel.models import *
from blog.models import *
from ocean import settings
from django.contrib.auth.decorators import login_required



def today(what='none'):  # get time
    x = datetime.now()
    if what == 'none':
        return x
    elif what == 'day':
        if len(str(x.day)) < 2:
            result = str('0') + str(x.day)
        else:
            result = x.day
        return result
    elif what == 'month':
        if len(str(x.month)) < 2:
            result = str('0') + str(x.month)
        else:
            result = x.month
        return result
    elif what == 'time':
        return x.time()
    elif what == 'year':
        return x.year

day = f"{today('year')}-{today('month')}-{today('day')}"

if Sales.objects.filter(day=day).exists():
    Sales.objects.filter(day=day)
    g_sales = 0
    taxes = 0
    discs = 0
    n_sales = 0
    total_s = 0
    for s in Sales.objects.filter(day=day):
        g_sales += s.gross_sales
        taxes += s.tax
        discs += s.discount
        n_sales += s.net_sales

    sales = {
        'gross_sales': babel.numbers.format_currency(g_sales, "₵ ", locale='en_US'),
        'tax': babel.numbers.format_currency(taxes, "₵ ", locale='en_US'),
        'discount': babel.numbers.format_currency(discs, "₵ ", locale='en_US'),
        'net_sales': babel.numbers.format_currency(n_sales, "₵ ", locale='en_US'),
        'total':babel.numbers.format_currency(n_sales - taxes, "₵ ", locale='en_US'),
    }

else:
    sales = {
        'gross_sales':0.00,
        'tax':0.00,
        'discount':0.00,
        'net_sales':0.00
    }



@login_required(login_url='/login/')
def index(request):
    current_user = request.user
    if current_user.is_active:
        return render(request, 'index.html')
    else:
        return redirect('login')

@login_required(login_url='/login/')
def all_issues(request):
    issues = questions.objects.all()
    context = {
        'page-title': 'ALL ISSUES',
        'issues': issues
    }
    return render(request, 'all_issues.html', context=context)

@login_required(login_url='/login/')
def view_issue(request, issue_id):
    issue = questions.objects.get(uni=issue_id)
    task_count = TaskHD.objects.filter(ref=issue_id).count()
    context = {
        'issue': issue,
        'task_count': task_count,
    }
    return render(request, 'view_issue.html', context=context)

@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def all_task(request):
    tasks = TaskHD.objects.all()
    prov = Providers.objects.all()

    context = {
        'tasks': tasks,
        'providers': prov,
        'page_title': "All Tasks",
        'sales':sales,
        'day':day,
        'domain': tags.objects.all()
    }
    return render(request, 'all_task.html', context=context)

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def to_scalate(request):
    x_counts = PendingEscalations.objects.all().values('provider').annotate(total=Count('provider')).order_by('total')
    context = {
        'x_count': x_counts
    }
    return render(request, 'to_escalate.html', context=context)

@login_required(login_url='/login/')
def escalate_detail(request, provider):
    prov_det = Providers.objects.get(provider_code=provider)
    issues = PendingEscalations.objects.filter(provider=provider)
    context = {
        'provider': prov_det,
        'questions': issues
    }
    return render(request, 'escalate_detail.html', context=context)

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def accessories(request):


    context = {
        'comm_tags': tags.objects.all(),
        'providers': Providers.objects.all()
    }
    return render(request, 'accessories.html', context=context)

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
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

        comment = answers(user=user.pk, question=ref,
                          ans="I have logged a task from your issue and it will be resolved soon")
        task_hd = TaskHD(entry_uni=ref, type='from_questions', ref=ref, owner=user.pk, title=title,
                         description=description)

        try:
            task_hd.save()
            comment.save()
            return HttpResponse(f'done%%reload')
        except Exception as e:
            return HttpResponse(f'error%%{e}')

# @login_required(login_url='/login/')
def view_task(request, task_id):
    context = {
        'taskHd': TaskHD.objects.get(entry_uni=task_id),
        'taskTran': TaskTrans.objects.filter(entry_uni=task_id),
        'domains':Providers.objects.all()
    }
    return render(request, 'issues.html', context=context)

@login_required(login_url='/login/')
def add_task_update(request):
    if request.method == 'POST':
        user = request.user
        form = request.POST
        title = form['title']
        body = form['body']
        entry = form['entry']

        try:
            TaskTrans(entry_uni=entry, tran_title=title, tran_descr=body, owner=user.pk).save()
            return redirect('view_task', task_id=entry)
        except Exception as e:
            return HttpResponse(e)

@login_required(login_url='/login/')
def new_task(request):
    if request.method == 'POST':
        form = request.POST
        title = form['title']
        body = form['body']
        domain = form['domain']
        owner = request.user.pk

        md_mix = f"{title} {owner} {body} {body}{request.user.pk}{request.user.username}"
        hash_object = hashlib.md5(md_mix.encode())
        md5_hash = hash_object.hexdigest()

        if TaskHD.objects.filter(entry_uni=md5_hash).exists():
            return redirect('all_task')
        else:
            try:
                TaskHD(entry_uni=md5_hash, title=title, description=body, owner=owner, ref='direct',
                       type='direct',domain=tags.objects.get(pk=domain)).save()
                return redirect('view_task', task_id=md5_hash)
            except Exception as e:
                return HttpResponse(f'error%%{e}')

    else:
        context = {
            'domain':tags.objects.all()
        }
        return render(request, 'new_task.html',context=context)

@login_required(login_url='/login/')
def update_task(request, entry_uni):
    if request.method == 'POST':
        form = request.POST
        entry_uni = form['entry']
        title = form['title']
        body = form['body']
        owner = request.user.pk

        try:
            TaskTrans(entry_uni=entry_uni, tran_title=title, tran_descr=body, owner=owner).save();
            return redirect('view_task', task_id=entry_uni)
        except Exception as e:
            return HttpResponse(f"Error : {e}")

    else:
        context = {
            'entry': TaskHD.objects.get(entry_uni=entry_uni),
        }
        return render(request, 'update_task.html', context=context)

@login_required(login_url='/login/')
def close_task(request):
    if request.method == 'GET':
        form = request.GET
        entry = form['entry']
        remarks = form['remarks']
        task_detail = TaskHD.objects.get(entry_uni=entry)

        try:
            TaskHD.objects.filter(entry_uni=entry).update(status=1)
            TaskTrans(entry_uni=entry, tran_title='Closing Remarks', tran_descr=remarks, owner=request.user.pk).save()
            if task_detail.type == 'from_questions':
                # comment in question
                answers(user=request.user.pk, question=task_detail.ref, ans=remarks).save()
            return HttpResponse(f'done%% task {entry} close')
        except Exception as e:
            TaskHD.objects.filter(entry_uni=entry).update(status=0)
            return HttpResponse(f'error%%{e}')

@login_required(login_url='/login/')
def export_issues(request):
    return None

@login_required(login_url='/login/')
def export_task(request):
    if request.method == 'GET':
        import nltk
        form = request.GET
        sort = form['sort']
        doc_type = form['doc_type']

        tasks = TaskHD.objects.filter(status__in=sort)
        if tasks.count() < 1:
            return HttpResponse('error%%There is no match for filter')
        else:
            if doc_type == 'csv':
                import csv
                # file = open(f"static/general/videos/export.csv")

                # field names
                fields = ['Type', 'Reference', 'Tite', 'Description', 'Date Created', 'Transactions']
                row = []

                response = HttpResponse(
                    content_type='text/csv',
                    headers={'Content-Disposition': 'attachment; filename="somefilename.csv"'},
                )
                writer = csv.writer(response)
                writer.writerow(fields)

                for task in tasks:
                    type = task.type
                    ref = task.ref
                    title = task.title
                    desc = task.description
                    date_c = task.added_on,
                    transactions = ""

                    # get trans
                    trans = TaskTrans.objects.filter(entry_uni=task.entry_uni)
                    if trans.count() > 0:
                        for tran in trans:
                            transactions += f"{tran.created_on} \n{tran.tran_title}\n{tran.tran_descr}\n\n"
                            soup = BeautifulSoup(transactions)
                            raw = soup.getText()

                            soup_desc = BeautifulSoup(desc)
                            desc_raw = soup_desc.getText()

                            writer.writerow([type, ref, title, desc_raw, date_c, raw])

                return response

@login_required(login_url='/login/')
def finder(request):
    if request.method == 'GET':
        form = request.GET
        target = form['for']
        query = form['query']

        if target == 'task':
            data = TaskHD.objects.filter(title__icontains=query)
            qs_json = serializers.serialize('json', data)
            return HttpResponse(qs_json, content_type='application/json')

@login_required(login_url='/login/')
def change_domain(request):
    if request.method == 'POST':

        form = request.POST
        curr_domain = form['curr_domain']
        new_domain = form['new_domain']
        reason = form['reason']
        task_uni = form['task_uni']



        new_domain_detail = Providers.objects.get(id=new_domain)
        old_domain_detail = Providers.objects.get(id=curr_domain)

        task_tran = TaskTrans(entry_uni=task_uni,tran_title=f'Domain Switch From {old_domain_detail.descr} To {new_domain_detail.descr}',tran_descr=reason,owner=request.user.pk)
        task_hd = TaskHD.objects.get(entry_uni=task_uni)
        task_hd.domain = Providers.objects.get(pk=new_domain)
        try:
            task_hd.save()
            task_tran.save()
            return HttpResponse('done%%Task Send to new domain')
        except Exception as e:
            return HttpResponse(f"error%%Error : {e}")

    else:
        return HttpResponse("error%%Invalid Form")


def test_suolution(request):
    if request.method == 'POST':
        form = request.POST
        task_uni = form['task_uni']
        to = form['to']
        body = form['body']
        recipient_list = [to]

        recipients = []
        rs = to.split(',')
        recipients.extend(rs)

        subject = form['subject']

        try:
            send_mail(subject, body, 'robolog', recipients, html_message=body,fail_silently=False)
            # update transactions
            Emails(sent_from='henrychase411@gmail.com',sent_to=to,subject=subject,body=body,email_type='task',ref=task_uni).save()
            TaskTrans(entry_uni=task_uni,tran_title='Testing',tran_descr=f"Send to {to} for testing \nBody:\n {body}").save()
            return redirect('view_task',task_id=task_uni)
        except Exception as e:
            return HttpResponse(f"Could Not Send Email {e}")

@login_required(login_url='/login/')
def task_filter(request):
    if request.method == 'GET':
        form = request.GET
        domain = form['domain']
        status = form['status']

        tasks = TaskHD.objects.filter(domain=domain,status=status)
        prov = Providers.objects.all()


        context = {
            'tasks': tasks,
            'providers': prov,
            'page_title': "All Tasks",
            'sales': sales,
            'day': day,
            'domain': tags.objects.all()
        }
        return render(request, 'all_task.html', context=context)