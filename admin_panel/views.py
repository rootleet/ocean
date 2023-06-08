# from bs4 import BeautifulSoup
import io
import random

import babel.numbers
# from unicodecsv import writer
import datetime
import hashlib

from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
# Create your views here.
from django.core import serializers
from django.core.mail import send_mail
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from fpdf import FPDF

from admin_panel.anton import push_notification, is_valid_password
from admin_panel.form import NewProduct, NewLocation, LogIn, NewTicket, UploadFIle, SignUp, NewOu, NewUM, NewSMSApi, \
    NewBulkSms
from admin_panel.models import *
from blog.models import *
from community.models import *
from django.views.decorators.csrf import csrf_exempt

from inventory.models import AssetGroup
from meeting.models import MeetingHD, MeetingTalkingPoints, MeetingTrans
from ocean.settings import EMAIL_HOST_USER


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

    n_sales = Sales.objects.filter(day=day).aggregate(Sum('net_sales'))['net_sales__sum']

    g_sales = Sales.objects.filter(day=day).aggregate(Sum('gross_sales'))['gross_sales__sum']

    taxes = Sales.objects.filter(day=day).aggregate(Sum('tax'))['tax__sum']

    discs = Sales.objects.filter(day=day).aggregate(Sum('discount'))['discount__sum']

    sales = {
        'gross_sales': babel.numbers.format_currency(g_sales, "₵ ", locale='en_US'),
        'tax': babel.numbers.format_currency(taxes, "₵ ", locale='en_US'),
        'discount': babel.numbers.format_currency(discs, "₵ ", locale='en_US'),
        'net_sales': babel.numbers.format_currency(n_sales, "₵ ", locale='en_US'),
        'total': babel.numbers.format_currency(n_sales - taxes, "₵ ", locale='en_US'),
    }

else:
    sales = {
        'gross_sales': 0.00,
        'tax': 0.00,
        'discount': 0.00,
        'net_sales': 0.00,
        'total': 0.00
    }


def is_logged_in(request):
    if request.user.is_active:

        pass
    else:
        print('hello')
        return redirect('login')


page = {
    'title': ''
}


## check fingurations
def check_config(pk):
    if UserAddOns.objects.filter(user=pk).count() != 1:
        return redirect('profile')


@login_required(login_url='/login/')
def index(request):
    # check user config
    # if request.user.is_authenticated:
    #     if UserAddOns.objects.filter(user=request.user.pk).count() != 1:
    #         messages.error(request, 'error%%Please configure your profile')
    #         return redirect('profile')

    notifications = {
        'unread': Notifications.objects.filter(owner=request.user, read=0).order_by('-pk'),
        'all': Notifications.objects.filter(owner=request.user).order_by('-pk')
    }
    page['title'] = 'Dashboard'
    my_issues = {
        'open': TicketHd.objects.filter(owner=request.user.pk, status=0).count(),
        'scheduled': TicketHd.objects.filter(owner=request.user.pk, status=1).count(),
        'close': TicketHd.objects.filter(owner=request.user.pk, status=3).count(),
    }
    context = {
        'notifications': notifications,
        'nav': True,
        'page': page,
        'my_issues': my_issues,
        'sales': sales,
        'usadons': UserAddOns.objects.filter(user=request.user.pk),
        'ussettings': UserSettings.objects.filter(user=request.user.pk)
    }
    return render(request, 'dashboard/index.html', context=context)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next = request.POST.get('next')
        User = get_user_model()

        ini = email
        # check if ini is an email or key
        if len(ini.split('@')) > 1:
            # email
            auth_req_user = User.objects.filter(email=ini)
            check_w = 'email'
        else:
            auth_req_user = User.objects.filter(username=ini)
            check_w = 'Username'

        user = User.objects.filter(email=email)

        if auth_req_user.count() == 1:
            if check_w == 'email':
                us = User.objects.get(email=ini)
            else:
                us = User.objects.get(username=ini)
            # us = User.objects.get(email=email)
            username = us.username
            auth = authenticate(request, username=username, password=password)

            if hasattr(auth, 'is_active'):
                auth_login(request, auth)
                return redirect(next)
            else:
                messages.error(request,
                               f"There is an error logging in, please check your credentials again or contact Administrator")
                return redirect('login')

            # auth_login(request, auth)
            # return redirect(next)

        else:
            messages.error(request,
                           f"Account does not exist with {check_w}")
            return redirect('login')

        # user = authenticate(request, email=email, password=password)
        # if user is not None:
        #     auth_login(request, user)
        #     return redirect(next)
        # else:
        #     messages.error(request,
        #                    f"There is an error logging in, please check your credentials again or contact Administrator")
        #     return redirect('login')
    # return render(request, 'login.html')


def login_process(request):
    if request.method == 'POST':
        form = LogIn(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            next = form.cleaned_data['next']

            # check if user exist
            user = authenticate(request, username=username, password=password)

            try:
                # check if user is valid
                if hasattr(user, 'is_active'):
                    auth_login(request, user)
                    # Redirect to a success page.
                    return redirect(next)
                else:
                    messages.error(request,
                                   f"There is an error logging in, please check your credentials again or contact Administrator")
                    return redirect('login')

            except Exception as e:
                messages.error(request, f"There was an error {e}")
                return redirect('login')

        else:
            return HttpResponse("Invalid Form")
    else:
        pass


def logout_view(request):
    logout(request)
    return redirect('home')


def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET' and 'next' in request.GET:
        next_page = request.GET['next']
    else:
        next_page = 'home'
    context = {
        'page_title': 'Ocean | Login',
        'form': LogIn(),
        'next': next_page
    }
    return render(request, 'dashboard/profile/loginv2.html', context=context)


def new_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    context = {
        'page_title': 'Ocean | Register',
        'form': LogIn()
    }
    return render(request, 'dashboard/profile/register.html', context=context)


def sign_up(request):
    if request.method == 'POST':

        form = SignUp(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            mobile = form.cleaned_data['mobile']
            position = request.POST['position']
            company = request.POST['company']

            # check if email exist
            if User.objects.filter(email=email).count() > 0:

                return HttpResponse(User.objects.filter(email=email).count())

            else:

                # generate username
                number = '{:03d}'.format(random.randrange(1, 9999))
                username = '{}{}'.format(last_name, number)

                pass_num = '{:03d}'.format(random.randrange(1, 999999))
                pass_w = '{}{}'.format(f"{last_name}", pass_num)

                # save username
                new_user_instance = User.objects.create_user(username=username, password=pass_w, email=email,
                                                             first_name=first_name, last_name=last_name)

                md_mix = f"{pass_w} {first_name} {last_name} {username} "
                hash_object = hashlib.md5(md_mix.encode())
                api_token = hash_object.hexdigest()

                try:
                    new_user_instance.save()
                    new_user_instance.is_active = False
                    AuthToken(user=new_user_instance, token=api_token).save()

                    use_ad_on = UserAddOns(user=new_user_instance, company=company,
                                           app_version=VersionHistory.objects.get(version=settings.APP_VERSION),
                                           position=position, phone=mobile)

                    md_mix = f" {first_name} {last_name} {username} "
                    hash_object = hashlib.md5(md_mix.encode())
                    resettoken = hash_object.hexdigest()

                    respwrd = PasswordResetToken(user=new_user_instance, token=resettoken, valid=1)
                    use_ad_on.save()
                    respwrd.save()

                    subject = 'ACCESS TO OCEAN'
                    message = f'Hi {first_name} {last_name}, thank you for registering in ocean. your username is {username} and password is {pass_w} logn at ocean t explore the power in collaboration '
                    message = f"Hello {first_name} {last_name}, an account has been created for you buy sneda at ocean. " \
                              f"<br>Use this platform to report and track your IT related." \
                              f"Reset your password and login with the link below <br>" \
                              f"http://ocean.snedaghana.loc/profile/restpwrod/{resettoken}/ "
                    email_from = settings.EMAIL_HOST_USER
                    try:
                        Emails(sent_from=email_from, sent_to=email, subject=subject, body=message, email_type='system',
                               ref='system').save()
                        # send_mail(subject, message, email_from, recipient_list)
                        # messages.error(request, "Please check your email to activate your account")

                        return redirect('all-users')
                    except Exception as e:
                        return HttpResponse(e)
                except Exception as e:
                    new_user_instance.delete()
                    messages.error(request, f"error%%Error Saving User {e}")
                    return HttpResponse(e)

        else:
            return HttpResponse(f"Invalid Form {form}")
    else:
        return HttpResponse("Unaccepted Form Method")


@login_required(login_url='/login/')
def all_issues(request):
    issues = questions.objects.all()
    context = {
        'page-title': 'ALL ISSUES',
        'issues': issues
    }
    return render(request, 'dashboard/all_issues.html', context=context)


@login_required(login_url='/login/')
def view_issue(request, issue_id):
    issue = questions.objects.get(uni=issue_id)
    task_count = TaskHD.objects.filter(ref=issue_id).count()
    context = {
        'issue': issue,
        'task_count': task_count,
    }
    return render(request, 'dashboard/view_issue.html', context=context)


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
    tasks = TaskHD.objects.filter(status=0).order_by('-pk')
    prov = Providers.objects.all()

    context = {
        'nav': True,
        'tasks': tasks,
        'providers': prov,
        'page_title': "All Tasks",
        'sales': sales,
        'day': day,
        'domain': tags.objects.all()
    }
    return render(request, 'dashboard/all_task.html', context=context)


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
    return render(request, 'dashboard/to_escalate.html', context=context)


def escalate_detail(request, provider):
    prov_det = Providers.objects.get(provider_code=provider)
    issues = PendingEscalations.objects.filter(provider=provider)
    context = {
        'provider': prov_det,
        'questions': issues
    }
    return render(request, 'dashboard/escalate_detail.html', context=context)


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
        'nav': True,
        'comm_tags': tags.objects.all(),
        'providers': Providers.objects.all(),
        'notomem': NotificationGroups.objects.all(),
        'assgrps': AssetGroup.objects.all()
    }
    return render(request, 'dashboard/accessories.html', context=context)


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
            save = tags(tag_code=code, tag_dec=description, provider=Providers.objects.get(pk=provider))
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


@login_required(login_url='/login/')
def view_task(request, task_id):
    page['title'] = 'Issues Details'
    context = {
        'page': page,
        'nav': True,
        'taskHd': TaskHD.objects.get(entry_uni=task_id),
        'taskTran': TaskTrans.objects.filter(entry_uni=task_id),
        'domains': tags.objects.all(),
        'branches': TaskBranchHD.objects.filter(task=TaskHD.objects.get(entry_uni=task_id)),
        'apis': SmsApi.objects.all()
    }
    return render(request, 'dashboard/issues.html', context=context)


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
        ref = 'direct'
        type = 'direct'
        try:
            ref = form['ref']
        except Exception as e:
            pass

        try:
            type = form['type']
        except Exception as e:
            pass

        domain = form['domain']
        own = form['owner']
        owner = User.objects.get(pk=own)

        md_mix = f"{title} {owner} {body} {body}{request.user.pk}{request.user.username}"
        hash_object = hashlib.md5(md_mix.encode())
        md5_hash = hash_object.hexdigest()

        if TaskHD.objects.filter(entry_uni=md5_hash).exists():
            messages.success(request, 'Task Exist')
            return redirect('all_task')
        else:
            try:
                TaskHD(entry_uni=md5_hash, title=title, description=body, owner=owner, ref=ref,
                       type=type, domain=tags.objects.get(pk=domain)).save()
                if type == 'TIK':
                    xticket = TicketHd.objects.get(pk=ref)
                    useradon = UserAddOns.objects.get(user=owner)
                    xticket.status = 1
                    sms_api = SmsApi.objects.get(sender_id='SNEDA SHOP')

                    text = f"Issues '{xticket.title}' has been logged by System Administrator. Issue will be checked " \
                           f"and resolved on time"
                    subject = f"Ticket {xticket.title} Closed"

                    push_notification(owner.pk, subject, text)

                    # Sms(api=sms_api, to=useradon.phone, message=text).save()

                    notification = Notifications(owner=User.objects.get(pk=xticket.owner.pk), type=2,
                                                 title='Ticket Longed',
                                                 descr=f"Your ticket {xticket.title} has been logged by an admin")

                    xticket.save()
                    notification.save()
                messages.success(request, "done%%Task Added")
                return redirect('view_task', task_id=md5_hash)
            except Exception as e:
                # delete notification
                if TaskHD.objects.filter(entry_uni=md5_hash).count() > 0:
                    TaskHD.objects.get(entry_uni=md5_hash).delete()

                return HttpResponse(f'error%%{e}')

    else:
        context = {
            'domain': tags.objects.all(),
            'users': User.objects.all()
        }
        return render(request, 'dashboard/new_task.html', context=context)


@login_required(login_url='/login/')
def update_task(request, entry_uni):
    if request.method == 'POST':
        form = request.POST
        entry_uni = form['entry']
        title = 'v2'
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
        return render(request, 'dashboard/update_task.html', context=context)


@login_required(login_url='/login/')
def close_task(request):
    user = request.user
    if request.method == 'GET':
        form = request.GET
        entry = form['entry']
        remarks = form['remarks']
        task_detail = TaskHD.objects.get(entry_uni=entry)
        task_type = task_detail.type
        ref = task_detail.ref

        try:
            TaskHD.objects.filter(entry_uni=entry).update(status=1)
            TaskTrans(entry_uni=entry, tran_title='Closing Remarks', tran_descr=remarks, owner=request.user.pk).save()
            if task_detail.type == 'from_questions':
                # comment in question
                answers(user=request.user.pk, question=task_detail.ref, ans=remarks).save()

            elif task_type == 'TIK':
                target_ticket = TicketHd.objects.get(pk=ref)

                ticket_owner = target_ticket.owner
                remark = f"Ticket has been closed with message '{remarks}'"
                subject = f"Ticket {target_ticket.title} Closed"

                TicketTrans(ticket=target_ticket, tran=remarks, user=user).save()
                text = f"Issue : {target_ticket.title}. Status : Closed. Message : {remark}"

                # Sms(api=sms_api, to=ticket_owner_adone.phone, message=text).save()
                push_notification(ticket_owner.pk, subject, text)

                t_now = TicketHd.objects.get(pk=ref)
                t_now.status = 2
                t_now.save()

            return HttpResponse(f'done%% task {entry} close')
        except Exception as e:
            TaskTrans(entry_uni=entry, tran_title='Closing Remarks', tran_descr=remarks, owner=request.user.pk).delete()
            TaskHD.objects.filter(entry_uni=entry).update(status=0)
            return HttpResponse(f'error%%{e}')


@login_required(login_url='/login/')
def export_issues(request):
    return None


@login_required(login_url='/login/')
def export_task(request):
    import re
    clean = re.compile('<.*?>')
    if request.method == 'GET':
        form = request.GET
        sort = form['sort']
        doc_type = form['doc_type']

        if doc_type == 'pdf':
            pdf = FPDF('L', 'mm', 'A4')
            pdf.add_page()

            pdf.set_font('Arial', 'B', 16)

            domains = tags.objects.all()
            for domain in domains:
                # get tasks
                task_hd = TaskHD.objects.filter(status__in=sort, domain=domain.pk)
                if task_hd.count() > 0:
                    pdf.set_font('Arial', 'B', 16)
                    pdf.set_text_color(40, 116, 166)
                    description = domain.tag_dec
                    pdf.multi_cell(0, 5, description, 0, 'L')
                    pdf.ln(2)
                    tcount = 0

                    for taskhd in task_hd:
                        uni = taskhd.entry_uni
                        trans = TaskTrans.objects.filter(entry_uni=uni)
                        if trans.count() > 0:
                            last = trans.last()
                            tran_time = str(last.created_on)
                            last_tran = f"{re.sub(clean, '', last.tran_descr)}"
                        else:
                            tran_time = 'NONE'
                            last_tran = "Not Attend To"

                        pdf.set_font('Arial', 'B', 10)
                        pdf.set_text_color(72, 201, 176)
                        pdf.multi_cell(0, 5, f"{tcount + 1} - {taskhd.title}", 0, 'L')

                        pdf.ln(2)

                        pdf.set_font('Arial', '', 8)
                        pdf.set_text_color(23, 32, 42)
                        pdf.set_font('','B')
                        pdf.multi_cell(0, 5, f"Description : {re.sub(clean, '', taskhd.description[0:300])} ", 0, 'L')
                        pdf.ln(1)
                        pdf.set_font('','')
                        ## pdf.set_text_color(229, 152, 102)
                        pdf.multi_cell(0, 5, f"Last Transaction : {re.sub(clean, '', last_tran)}", 0, 'L')
                        pdf.multi_cell(0, 5, f"Transaction Time : {tran_time}", 0, 'L')
                        tcount += 1
                        pdf.ln(2)

                    pdf.ln(5)

        md_mix = f"{request.user.username}"
        hash_object = hashlib.md5(md_mix.encode())
        file_name = hash_object.hexdigest()
        pdf.output(f'static/general/docs/{file_name}.pdf', 'F')

        return HttpResponse(f'done%%{file_name}')


# @login_required(login_url='/login/')
def finder(request):
    if request.method == 'GET':
        form = request.GET
        target = form['for']
        query = form['query']

        if target == 'task':
            data = TaskHD.objects.filter(title__icontains=query)
            qs_json = serializers.serialize('json', data)
            return HttpResponse(qs_json, content_type='application/json')

        elif target == 'item_for_adjust':
            q = form['query']
            data = ProductMaster.objects.filter(descr__icontains=q)
            qs_json = serializers.serialize('json', data)
            return HttpResponse(qs_json, content_type='application/json')

        elif target == 'get_product':
            q = form['query']
            data = ProductMaster.objects.filter(barcode=q)
            qs_json = serializers.serialize('json', data)
            return HttpResponse(qs_json, content_type='application/json')

        elif target == 'get_prod_packing':
            q = form['query']

            data = ProductPacking.objects.filter(product=ProductMaster.objects.get(barcode=q))

            if data.count() > 0:
                # x_json = serializers.serialize('json', obj)
                qs_json = serializers.serialize('json', data)
                return HttpResponse(qs_json, content_type='application/json')
            else:
                return HttpResponse('NO DATA')

        else:
            return HttpResponse('unknown')


@login_required(login_url='/login/')
def change_domain(request):
    if request.method == 'POST':

        form = request.POST
        curr_domain = form['curr_domain']
        new_domain = form['new_domain']
        reason = form['reason']
        task_uni = form['task_uni']

        # new_domain_detail = tags.objects.get(id=new_domain)
        # old_domain_detail = tags.objects.get(id=curr_domain)

        task_tran = TaskTrans(entry_uni=task_uni, tran_title=f'Domain Switch From {curr_domain} To {new_domain}',
                              tran_descr=reason, owner=request.user.pk)
        task_hd = TaskHD.objects.get(entry_uni=task_uni)
        # return HttpResponse(new_domain)
        task_hd.domain = tags.objects.get(pk=new_domain)
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
            send_mail(subject, body, 'robolog', recipients, html_message=body, fail_silently=False)
            # update transactions
            Emails(sent_from='henrychase411@gmail.com', sent_to=to, subject=subject, body=body, email_type='task',
                   ref=task_uni, status=1).save()
            TaskTrans(entry_uni=task_uni, tran_title='Testing',
                      tran_descr=f"Send to {to} for testing \nBody:\n {body}").save()
            return redirect('view_task', task_id=task_uni)
        except Exception as e:
            return HttpResponse(f"Could Not Send Email {e}")


@login_required(login_url='/login/')
def task_filter(request):
    if request.method == 'GET':
        form = request.GET
        domain = form['domain']
        status = form['status']

        tasks = TaskHD.objects.filter(domain=domain, status=status).order_by('-pk')
        prov = Providers.objects.all()

        context = {
            'nav': True,
            'tasks': tasks,
            'providers': prov,
            'page_title': "All Tasks",
            'sales': sales,
            'day': day,
            'domain': tags.objects.all()
        }
        return render(request, 'dashboard/all_task.html', context=context)


def emails(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all()
    page['title'] = "Email Setups"
    context = {
        'nav': True,
        'pahe': page,
        'comm_tags': tags.objects.all(),
        'email_groups': EmailGroup.objects.all(),
        'emails': Emails.objects.all(),
        'email_address': NotificationGroups.objects.all()
    }
    return render(request, 'dashboard/emails.html', context=context)


def add_notification_mem(request):
    if request.method == 'POST':
        form = request.POST
        full_name = form['full_name']
        email = form['email']
        phone = form['phone']
        emg = form['email_group']
        email_group = EmailGroup.objects.get(pk=emg)

        try:
            NotificationGroups(full_name=full_name, email_addr=email, mobile_number=phone, group=email_group).save()
            messages.error(request, f"{email} Added to {email_group.group_name}")
            return redirect('emails')
        except Exception as e:
            messages.error(request, f"There is an error adding email {e}")
            return redirect('emails')


def send_mail(request, task_id):
    if request.method == 'POST':
        form = request.POST
        group = form['group']
        entry = form['entry']
        subject = form['subject']
        body = form['body']

        # get all group member
        group_member = NotificationGroups.objects.filter(group=EmailGroup.objects.get(pk=group))
        group_email_addr = ''
        if group_member.count() > 0:
            for memeber in group_member:
                email_address = memeber.email_addr
                try:
                    group_email_addr += f" {email_address}"
                    email_address = memeber.email_addr
                    Emails(sent_from='Admin', sent_to=email_address, subject=subject, body=body, email_type='task',
                           ref=entry).save()
                except Exception as e:
                    print(f"Could Not sent on {e}")

            TaskTrans(entry_uni=entry, tran_title='Send Mail',
                      tran_descr=f"Email has been send to {group_email_addr} with message {body}",
                      owner=request.user.pk).save()
        # insert into notification
        messages.error(request, f"Email Sceduled to be sent to {group_email_addr}")
        return redirect('view_task', task_id=entry)


    else:
        context = {
            'entry': TaskHD.objects.get(entry_uni=task_id),
            'groups': EmailGroup.objects.all()
        }
        return render(request, 'dashboard/send_task_mail.html', context=context)


def auto(request, tool):
    if tool == 'mail_sync':
        from django.core import mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        errors = ''
        passes = ''

        if Emails.objects.filter(status=0).count() > 0:

            for email in Emails.objects.filter(status=0):
                recipient = email.sent_to
                subject = email.subject
                sent_from = email.sent_from
                body = email.body
                this_email = Emails.objects.filter(pk=email.pk)
                email_type = email.email_type
                email_ref = email.ref

                html_message = render_to_string('dashboard/mail_template.html', {'body': body})
                plain_message = strip_tags(html_message)
                from_email = EMAIL_HOST_USER
                to = recipient
                try:

                    mail.send_mail(subject, body, from_email, [to], html_message=body)
                    # update transactions
                    q = Emails.objects.get(pk=email.pk)
                    q.status = 1
                    q.status_message = 'Email Sent'
                    q.save()

                    if email_type == 'task':
                        TaskTrans(entry_uni=email_ref, tran_title='Send Mail', tran_descr=body, owner=0)

                    passes += f"Email Sent to {request} \n"
                except Exception as e:
                    errors += f" Could not send email to {recipient} because {e}"

            return HttpResponse(f"Passes : {passes} \n Failed : {errors}")
        else:

            return HttpResponse(f"No EMail To Send")

    elif tool == 'ajax':
        if request.method == 'GET':
            form = request.GET
            function = form['function']

            if function == 'prod_subs':
                group = form['group']
                # get sub groups of group
                data = ProductGroupSub.objects.filter(group=ProductGroup.objects.get(pk=group))
                qs_json = serializers.serialize('json', data)
                return HttpResponse(qs_json, content_type='application/json')


def post_form(request):
    if request.method == 'POST':
        form = request.POST
        function = form['function']

        if function == 'new_location':
            form = NewLocation(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    return redirect('loc_master')
                except Exception as e:
                    messages.error(redirect, f"Could not save location {e}")
                    return redirect('loc_master')
            else:
                return HttpResponse(f"INVALID FORM {form}")


        else:
            return HttpResponse('INVALID FUNCTION')

    else:
        return HttpResponse('INVALID METHOD')


def save_email_group(request):
    if request.method == 'POST':
        form = request.POST
        name = form['name']
        tag = form['tag']
        description = form['description']

        try:
            EmailGroup(
                group_name=name,
                def_domain=tags.objects.get(pk=tag),
                description=description,
                created_by=request.user.pk
            ).save()
            messages.error(request, f"Group Saved")
            return redirect('emails')
        except Exception as e:
            messages.error(request, f"Could Not Save Group {e}")
            return redirect('emails')


def inventory_tools(request):
    page['title'] = 'Inventory Add-Ons'
    context = {
        'nav': True,
        'page_title': 'Inventory Tools',
        'banks': BankAccounts.objects.filter(status=1),
        'suppliers': SuppMaster.objects.filter(status=1),
        'groups': ProductGroup.objects.filter(status=1),
        'packing': PackingMaster.objects.filter(status=1),
        'page': page
    }
    return render(request, 'dashboard/suppliers/inventory_tools.html', context=context)


def accounts(request):
    context = {
        'page_title': 'Accounts'
    }
    return render(request, 'dashboard/accounts/acct_home.html', context=context)


def tax_master(request):
    # if posting a form
    if request.method == 'POST':
        form = request.POST
        function = form['function']  # function decides what to do
        if function == 'save_new_tax':
            # save new tax component
            tax_code = form['tax_code']
            tax_description = form['tax_description']
            rate = form['rate']
            try:

                if TaxMaster.objects.filter(tax_code=tax_code).count() == 0:
                    TaxMaster(tax_code=tax_code, tax_description=tax_description, tax_rate=rate,
                              created_by=request.user.pk).save()
                    messages.success(request, 'done%%New Tax Added')

                else:
                    messages.success(request, 'error%%Duplicate Tax Code')

                return render(request, 'dashboard/accounts/tax_master.htm')

            except Exception as e:

                messages.success(request, f'error%%{e}')
                return render(request, 'dashboard/accounts/tax_master.htm')

        else:
            # render tax master page
            return render(request, 'dashboard/accounts/tax_master.htm')

    else:
        # show all tax
        context = {
            'page_title': 'Tax Master',
            'taxes': TaxMaster.objects.all().order_by('-pk')
        }
        return render(request, 'dashboard/accounts/tax_master.htm', context=context)


def bank_master(request):
    context = {
        'page_title': 'Bank Master',
        'accounts': BankAccounts.objects.all()
    }
    return render(request, 'dashboard/accounts/bank-master.html', context=context)


def bank_posts(request):
    if request.method == 'POST':
        import random
        import string
        form = request.POST
        function = form['function']

        if function == 'new_account':
            account_name = form['account_name']
            description = form['description']
            acct_serial = file_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

            try:
                BankAccounts(acct_name=account_name, acct_serial=acct_serial, acct_descr=description).save()
                messages.error(request, f"done%%Account created with serial {acct_serial}")
            except Exception as e:
                messages.error(request, f"error%%Could not create account : {e}")

    # redirect after anything
    return redirect('bank-master')


def save_supplier(request):
    if request.method == 'POST':
        form = request.POST
        company = form['company']
        contact_person = form['contact_person']
        purch_group = form['domain']
        origin = form['origin']
        email = form['email']
        mobile = form['phone']
        city = form['city']
        street = form['street']
        taxable = form['taxable']
        bank_acct = form['account']

        try:
            SuppMaster(company=company, contact_person=contact_person, purch_group=purch_group, origin=origin,
                       email=email,
                       mobile=mobile, city=city, street=street, taxable=taxable,
                       bank_acct=BankAccounts.objects.get(pk=bank_acct), created_by=request.user.pk).save()
            messages.error(request, f"done%%Supplier {company} Added")
            return redirect('suppliers')
        except Exception as e:
            messages.error(request, f"error%%Could not save supplier {e}")
            return redirect('suppliers')


@login_required(login_url='/login/')
def products(request):
    if ProductMaster.objects.filter().count() < 1:
        # redirect to new products creation
        messages.error(request, f"done%%Inventory is empty, Create an item")
        return redirect('new-product')
    context = {
        'nav': True,
        'page_title': 'Products Master | View', 'products': ProductMaster.objects.all()
    }
    return render(request, 'dashboard/products/view.html', context=context)


@login_required(login_url='/login/')
def new_products(request):
    is_logged_in(request)
    groups = ProductGroup.objects.filter(status=1)
    taxes = TaxMaster.objects.filter(status=1)
    packs = PackingMaster.objects.filter(status=1)
    supps = SuppMaster.objects.filter(status=1)

    if groups.count() < 1:
        messages.error(request, "done%%Create groups before you can add products")
        return redirect('inventory_tools')

    if supps.count() < 1:
        messages.error(request, "done%%Create or enable at least one supplier before you can add products")
        return redirect('inventory_tools')

    if ProductGroupSub.objects.filter(status=1).count() < 1:
        messages.error(request, "done%%Create or enable at least one sub group before you can add products")
        return redirect('inventory_tools')

    if taxes.count() < 1:
        messages.error(request, "done%%Create or enable at least one tax group before you can add products")
        return redirect('inventory_tools')

    if packs.count() < 1:
        messages.error(request, "done%%Create or enable at least one packaging before you can add products")
        return redirect('inventory_tools')

    context = {
        'nav': True,
        'page_title': 'Products Master | New',
        'groups': groups, 'taxes': taxes, 'packs': packs, 'supps': supps
    }
    return render(request, 'dashboard/products/new.html', context=context)


@login_required(login_url='/login/')
def save_group(request):
    if request.method == 'POST':
        form = request.POST
        group_name = form['group_name']

        try:
            ProductGroup(descr=group_name, created_by=request.user.pk).save()
            messages.error(request, f"New Group {group_name} Saved")
        except Exception as e:
            messages.error(request, f"Error saving new group {group_name} : {e}")

    return redirect('inventory_tools')


@login_required(login_url='/login/')
def save_sub_group(request):
    if request.method == 'POST':
        form = request.POST
        descr = form['descr']
        group = form['group']

        try:
            ProductGroupSub(group=ProductGroup.objects.get(pk=group), descr=descr, created_by=request.user.pk).save()
            messages.error(request, f"News subgroup added")
        except Exception as e:
            messages.error(request, f"Failed adding sub group : {e}")

    return redirect('inventory_tools')


@login_required(login_url='/login/')
def save_packing(request):
    if request.method == 'POST':
        form = request.POST
        code = form['code']
        description = form['description']

        try:
            PackingMaster(code=code, descr=description, created_by=request.user.pk).save()
            messages.error(request, f"News Packing {description} added")
        except Exception as e:
            messages.error(request, f"Failed adding Packing: {e}")

    return redirect('inventory_tools')


@login_required(login_url='/login/')
def suppliers(request):
    context = {
        'suppliers': SuppMaster.objects.all(),
        'accounts': BankAccounts.objects.all()
    }
    return render(request, 'dashboard/accounts/suppiers.html', context=context)


def save_new_product(request):
    form = NewProduct(request.POST, request.FILES)
    if form.is_valid():
        if ProductMaster.objects.filter(barcode=form.cleaned_data['barcode']).count() > 1:
            messages.error("Barcode Exist")
            return redirect('products')
        try:
            if form.save():
                # validate packing for products creation
                obj = ProductMaster.objects.latest('id')
                purch_un = request.POST['purch_un']
                purch_qty = request.POST['purch_qty']
                ass_un = request.POST['ass_un']
                ass_qty = request.POST['ass_qty']

                ProductPacking(product=obj, packing_un=PackingMaster.objects.get(pk=purch_un), pack_qty=purch_qty,
                               packing_type='P').save()
                ProductPacking(product=obj, packing_un=PackingMaster.objects.get(pk=ass_un), pack_qty=ass_qty,
                               packing_type='A').save()

                messages.error(request, 'done%%Item Added')

            return redirect('products')

        except Exception as e:
            messages.error(request, f'error%%{e}')
            return HttpResponse(e)

    else:
        return HttpResponse(f'Invalid Form {form}')


def adjust_product_qty(request, p):
    if request.method == 'POST':
        form = request.POST
        pk = form['pk']
        tran_qty = form['qty']
        doc = form['type']
        doc_ref = "ADJUSTMENT"

        ProductTrans(doc=doc, doc_ref=doc_ref, tran_qty=tran_qty, product=ProductMaster.objects.get(pk=pk)).save()
        messages.error(request, 'done%%Product Received')

        return redirect('products')

    else:
        product = ProductMaster.objects.get(pk=p)
        context = {
            'page_title': f'Received {product.descr}', 'product': product
        }
        return render(request, 'dashboard/products/adjust.html', context=context)


@login_required(login_url='/login/')
def adjustment(request):
    if AdjHd.objects.all().count() == 0:
        messages.success(request, "No Adjustment Entry")
        return redirect('new_adjustment')

    else:
        context = {
            'nav': True,
            'last': AdjHd.objects.last().pk,
            'page_title': 'Adjustment'
        }
        return render(request, 'dashboard/products/adjustment.html', context=context)


@login_required(login_url='/login/')
def new_adjustment(request):
    context = {
        'nav': True,
        'page_title': 'Add Adjustment',
        'locs': Locations.objects.all()
    }
    return render(request, 'dashboard/products/new_adjustment.html', context=context)


@csrf_exempt
def api(request, module, action):
    global status, message
    import json
    status = 000
    message = 000

    try:
        json_data = json.loads(request.body)
    except Exception as e:
        pass

    if module == 'auth':
        api_token = action
        token_filter = AuthToken.objects.filter(token=api_token)
        if token_filter.count() == 1:
            token_d = AuthToken.objects.get(token=api_token)
            username = token_d.user.username
            password = token_d.user.password

            # login
            user = authenticate(request, username=username, password=password)

            try:
                # check if user is valid
                if hasattr(user, 'is_active'):
                    auth_login(request, user)
                    # Redirect to a success page.
                    return redirect('home')
                else:
                    messages.error(request,
                                   f"There is an error logging in, please check your credentials again or contact Administrator")
                    return redirect('login')

            except Exception as e:
                messages.error(request, f"There was an error {e}")
                return redirect('login')

        else:
            return HttpResponse('INVALID TOKEN')

    elif module == 'user':
        if action == 'delete':

            pk = json_data['user']

            user = User.objects.get(pk=pk)
            try:
                user.delete()
                if UserAddOns.objects.filter(user=pk).count() > 0:
                    UserAddOns.objects.get(user=pk).delete()
                status = 200
                message = "User Deleted"
            except Exception as e:
                status = 505
                message = e




    elif module == 'adjustment':

        if action == 'new_tran':

            json_data = json.loads(request.body)

            print(json_data)
            # inititialising json object
            parent = json_data['parent']
            line = json_data['line']
            packing = json_data['packing']
            quantity = json_data['quantity']
            total = json_data['total']
            product = json_data['product']

            # insert into database
            try:
                AdjTran(parent=AdjHd.objects.get(pk=parent), line=line,
                        product=ProductMaster.objects.get(barcode=product), packing=packing, quantity=quantity,
                        total=total).save()
                # ProductTrans(doc='ADJ', doc_ref=parent, tran_qty=total,
                #              product=ProductMaster.objects.get(pk=ProductMaster.objects.get(barcode=product)).pk).save()

                messages.error(request, 'done%%Product Received')

                status = 202
                message = 'Data Added'

            except Exception as error:
                status = 505
                message = str(error)

            return JsonResponse({'status': status, 'message': message}, safe=False)

        elif action == 'new_hd':
            # save new adjustment hd
            json_data = json.loads(request.body)
            try:

                remark = json_data['remark']
                loc = Locations.objects.get(pk=json_data['loc'])
                AdjHd(remark=remark, loc=loc).save()

                last = AdjHd.objects.last()
                id = last.pk
                status = 200
                message = id

            except Exception as e:
                status = 505
                message = str(e)

            return JsonResponse({'status': status, 'message': message}, safe=False)

        elif action == 'get_hd':

            json_data = json.loads(request.body)

            hd = json_data['pk']

            if AdjHd.objects.filter(pk=hd).count() == 1:
                data = AdjHd.objects.get(pk=hd)
                prev_count = AdjHd.objects.all().filter(pk__lt=hd).count()
                next_count = AdjHd.objects.all().filter(pk__gt=hd).count()

                next = 0
                x_p = 0
                y_p = 0

                if prev_count > 0:
                    prevx = AdjHd.objects.all().filter(pk__lt=hd)
                    for x in prevx:
                        print(x.pk)
                        x_p = str(x.pk)
                if next_count > 0:
                    next = AdjHd.objects.all().filter(pk__gt=hd)[:1]
                    for y in next:
                        print(y.pk)
                        y_p = str(y.pk)

                print()
                print(f"PREV {x_p}")
                print(f"NEXT {next}")
                print(prev_count)
                print()

                status = 202
                message = {
                    'entry_no': f"ADJ000{hd}",
                    'remark': data.remark,
                    'date': data.created_on,
                    'loc': f"{data.loc.code} - {data.loc.descr}",
                    'status': data.status,
                    'next_count': next_count,
                    'next': y_p,
                    'prev_count': prev_count,
                    'prev': x_p
                }

                # print()
                # print(f"CUST MESSAGE {message}")
                # print()

            else:
                status = 404
                message = 'Adjustment HD Not Found'
            return JsonResponse({'status': status, 'message': message}, safe=False)

        elif action == 'get_tran':
            json_data = json.loads(request.body)

            print()
            print(f"JSON DATA {request.body}")
            print()

            hd = json_data['pk']

            if AdjTran.objects.filter(parent=hd).count() > 0:
                x_tran = AdjTran.objects.filter(parent=hd)
                message = []
                for x in x_tran:
                    this_line = {
                        'line': x.line,
                        'barcode': x.product.barcode,
                        'description': x.product.descr,
                        'quantity': x.quantity,
                        'pack_qty': x.packing,
                        'total': x.total
                    }
                    message.append(this_line)

                status = 202
                print()
                print(f"CUST MESSAGE {message}")
                print()

            else:
                status = 404
                message = 'No Trans'
            return JsonResponse({'status': status, 'message': message}, safe=False)

        elif action == 'approve':
            json_data = json.loads(request.body)

            hd = json_data['pk']

            if AdjHd.objects.filter(pk=hd).count() > 0:
                hd_details = AdjHd.objects.get(pk=hd)
                loc = Locations.objects.get(pk=hd_details.loc.pk)

                trans = AdjTran.objects.filter(parent=hd)
                message = ''
                add_err = 0
                for tran in trans:
                    doc = 'AD'
                    doc_ref = hd
                    product = ProductMaster.objects.get(pk=tran.product.pk)
                    tran_qty = tran.quantity

                    try:
                        ProductTrans(doc=doc, doc_ref=doc_ref, product=product, tran_qty=tran_qty, loc=loc).save()
                    except Exception as e:
                        add_err = + 1
                        message += f"<p>{e}</p>"

                if add_err > 0:
                    # delete transaction
                    ProductTrans.objects.filter(doc='ADJ', doc_ref=hd).delete()
                    status = 505
                    message = message
                else:
                    x_hd = AdjHd.objects.get(pk=hd)
                    x_hd.status = 1
                    x_hd.save()
                    message = 'document save'
                    status = 202

            else:
                status = 404
                message = 'No Trans'
                messages.error(request, message)
            return JsonResponse({'status': status, 'message': message}, safe=False)


        else:
            return HttpResponse('Unknown action')

    elif module == 'transfer':
        if action == 'new_hd':
            json_data = json.loads(request.body)
            try:

                remark = json_data['remark']
                loc_fr = Locations.objects.get(pk=json_data['from'])
                loc_to = json_data['to']

                TransferHD(remark=remark, loc_fr=loc_fr, loc_to=loc_to).save()

                last = TransferHD.objects.last()
                id = last.pk
                status = 200
                message = id

            except Exception as e:
                status = 505
                message = str(e)

            return JsonResponse({'status': status, 'message': message}, safe=False)

        if action == 'new_tran':

            json_data = json.loads(request.body)

            print(json_data)
            # inititialising json object
            parent = json_data['parent']
            line = json_data['line']
            packing = json_data['packing']
            quantity = json_data['quantity']
            total = json_data['total']
            product = json_data['product']

            # insert into database
            try:
                TransferTran(parent=TransferHD.objects.get(pk=parent), line=line,
                             product=ProductMaster.objects.get(barcode=product), packing=packing, quantity=quantity,
                             total=total).save()

                messages.error(request, 'done%%Transaction Saved')

                status = 202
                message = 'Transfer Saved'

            except Exception as error:
                status = 505
                message = str(error)

            return JsonResponse({'status': status, 'message': message}, safe=False)

        elif action == 'get_hd':

            json_data = json.loads(request.body)
            hd = json_data['pk']

            if TransferHD.objects.filter(pk=hd).exists():

                tran_hd = TransferHD.objects.get(pk=hd)
                to = Locations.objects.get(pk=tran_hd.loc_to)

                prev_count = TransferHD.objects.all().filter(pk__lt=hd).count()
                next_count = TransferHD.objects.all().filter(pk__gt=hd).count()

                next = 0
                x_p = 0
                y_p = 0

                if prev_count > 0:
                    prevx = TransferHD.objects.all().filter(pk__lt=hd)
                    for x in prevx:
                        print(x.pk)
                        x_p = str(x.pk)
                if next_count > 0:
                    next = TransferHD.objects.all().filter(pk__gt=hd)[:1]
                    for y in next:
                        print(y.pk)
                        y_p = str(y.pk)

                message = {
                    'entry_no': tran_hd.pk,
                    'date': tran_hd.created_on,
                    'remark': tran_hd.remark,
                    'from_code': tran_hd.loc_fr.code,
                    'from_descr': tran_hd.loc_fr.descr,
                    'to': to.code,
                    'to_descr': to.descr,
                    'status': tran_hd.status,
                    'next_count': next_count,
                    'next': y_p,
                    'prev_count': prev_count,
                    'prev': x_p
                }


            else:
                message = 'Document Does Not Exist'

            return JsonResponse({'status': status, 'message': message}, safe=False)

        elif action == 'get_tran':
            json_data = json.loads(request.body)

            print()
            print(f"JSON DATA {request.body}")
            print()

            hd = json_data['pk']

            if TransferHD.objects.filter(pk=hd).exists():
                transfer_tran = TransferTran.objects.filter(parent=hd)
                message = []
                for x in transfer_tran:
                    this_line = {
                        'line': x.line,
                        'barcode': x.product.barcode,
                        'description': x.product.descr,
                        'quantity': x.quantity,
                        'pack_qty': x.packing,
                        'total': x.total
                    }
                    message.append(this_line)

                status = 202
                print()
                print(f"CUST MESSAGE {message}")
                print()

            else:
                status = 404
                message = 'No Trans'
            return JsonResponse({'status': status, 'message': message}, safe=False)


        elif action == 'approve':

            json_data = json.loads(request.body)

            hd = json_data['pk']

            if TransferHD.objects.filter(pk=hd).exists():

                hd_details = TransferHD.objects.get(pk=hd)

                loc_fr = Locations.objects.get(pk=hd_details.loc_fr.pk)
                loc_to = Locations.objects.get(pk=hd_details.loc_to)

                trans = TransferTran.objects.filter(parent=hd)

                message = ''

                add_err = 0

                for tran in trans:

                    doc = 'TR'

                    doc_ref = hd

                    product = ProductMaster.objects.get(pk=tran.product.pk)

                    tran_qty = tran.total
                    tran_qty_fro = tran_qty * 2

                    try:

                        ProductTrans(doc=doc, doc_ref=doc_ref, product=product, tran_qty=tran_qty, loc=loc_to).save()
                        ProductTrans(doc=doc, doc_ref=doc_ref, product=product, tran_qty=tran_qty - tran_qty_fro,
                                     loc=loc_fr).save()

                    except Exception as e:

                        add_err = + 1

                        message += f"<p>{e}</p>"

                if add_err > 0:

                    # delete transaction

                    ProductTrans.objects.filter(doc='TR', doc_ref=hd).delete()

                    status = 505

                    message = message

                else:

                    try:
                        xxm = TransferHD.objects.get(pk=hd)

                        xxm.status = 1

                        xxm.save()

                        message = 'Document Approved'

                        status = 202

                    except Exception as e:
                        message = 'Could Not Update Header'

                        status = 404


            else:

                status = 404

                message = 'No Trans'

                messages.error(request, message)

            return JsonResponse({'status': status, 'message': message}, safe=False)

    elif module == 'issues':

        x_json = json.loads(request.body)  # JSON DATA

        if action == 'newBranch':  # creating new branch
            branch_name = x_json['branch_name']
            parent_task = x_json['parent_task'],
            description = x_json['description']

            md_mix = f"{branch_name} {parent_task} {description} {datetime.date}"
            hash_object = hashlib.md5(md_mix.encode())
            line_uni = hash_object.hexdigest()

            tas_id = int(list(parent_task)[0])

            task = TaskHD.objects.get(pk=tas_id)

            owner = request.user.pk
            owner = 1

            try:
                TaskBranchHD(br_name=branch_name, descr=description, task=task, md_hash=line_uni).save()
                status = 200
                message = 'Branch Created'
            except Exception as e:
                status = 505
                message = e
                # return HttpResponse(e)
            return JsonResponse({'status': status, 'message': message}, safe=False)

        elif action == 'updateBranch':
            br = x_json['br']
            descr = x_json['descr']

            try:
                TaskBranchTran(parent=TaskBranchHD.objects.get(pk=br), descr=descr,
                               owner=User.objects.get(pk=request.user.pk)).save()
                status = 200
                message = 'Updated Added'
            except Exception as e:
                status = 505
                message = e


    elif module == 'products':
        if action == 'get_stock':
            json_data = json.loads(request.body)
            product = json_data['pk']
            message = []
            for loc in Locations.objects.all():

                if ProductTrans.objects.filter(product=ProductMaster.objects.get(pk=product), loc=loc.pk).aggregate(
                        Sum('tran_qty'))['tran_qty__sum'] is None:
                    total = 0
                else:
                    total = \
                        ProductTrans.objects.filter(product=ProductMaster.objects.get(pk=product),
                                                    loc=loc.pk).aggregate(
                            Sum('tran_qty'))['tran_qty__sum']

                this_stock = {
                    'loc': loc.code,
                    'loc_descr': loc.descr,
                    'stock': total
                }

                message.append(this_stock)

            status = 202
            # message = {
            #     'loc1':total,
            #     'loc2':300
            # }

        return JsonResponse({'status': status, 'message': message}, safe=False)

    elif module == 'meeting':

        if action == 'tran':  ## new meeting tran
            meeting_pk = json_data['meeting']
            meeting = MeetingHD.objects.get(pk=meeting_pk)

            talking_point_pk = json_data['talking_point']
            talking_point = MeetingTalkingPoints.objects.get(pk=talking_point_pk)

            tran = json_data['tran']

            user = User.objects.get(pk=request.user.pk)

            try:
                MeetingTrans(meeting=meeting, talking_point=talking_point, descr=tran, owner=user).save()
                status = 200
                message = "Tran Added"
            except Exception as e:
                status = 500
                message = e

        # get meeting trans
        elif action == 'GrtTan':
            meeting_pk = json_data['meeting']
            meeting = MeetingHD.objects.get(pk=meeting_pk)
            trans = MeetingTrans.objects.filter(meeting=meeting)

            to_return = []
            if trans.count() > 0:
                status = 200
                for tran in trans:
                    this_line = {
                        'point': tran.talking_point.title,
                        'descr': tran.descr,
                        'created_date': tran.created_date,
                        'created_time': tran.created_time,
                        'owner': f"{tran.owner.first_name} {tran.owner.last_name}"
                    }

                    to_return.append(this_line)
            else:
                message = 'No RECORD'

            message = to_return

        # start meeting
        elif action == 'start':
            meeting_pk = json_data['meeting']
            try:
                meeting = MeetingHD.objects.get(pk=meeting_pk)
                meeting.status = 1
                meeting.save()
                status = 200
                message = "Started"
            except Exception as e:
                status = 500
                message = e

        # end
        elif action == 'end':
            meeting_pk = json_data['meeting']
            try:
                meeting = MeetingHD.objects.get(pk=meeting_pk)
                meeting.status = 3
                meeting.save()
                status = 200
                message = "Started"
            except Exception as e:
                status = 500
                message = e

        else:
            message = f"UNKNOWN ACTION {action}"

    else:
        status = 505
        message = 'UNKNOWN MODEL'

    return JsonResponse({'status': status, 'message': message}, safe=False)


def loc_master(request):
    context = {
        'page_title': 'Location Master',
        'locations': Locations.objects.all()
    }
    return render(request, 'dashboard/company/loc_master.html', context=context)


@login_required()
def transfer(request):
    if TransferHD.objects.filter().count() < 1:
        return redirect('new_transfer')
    else:
        context = {
            'nav': True,
            'last': TransferHD.objects.last().pk,
            'page_title': 'Transfer',
            'locations': Locations.objects.all()
        }

        return render(request, 'dashboard/products/transfer.html', context=context)


@login_required()
def new_transfer(request):
    context = {
        'nav': True,
        'page_title': 'New Transfer',
        'locations': Locations.objects.all()
    }
    return render(request, 'dashboard/products/new_transfer.html', context=context)


@login_required()
def grn_entries(request):
    if GrnHd.objects.filter().count() < 1:
        return redirect('new_grn')
    else:
        context = {
            'nav': True,
            'last': TransferHD.objects.last().pk,
            'page_title': 'Transfer',
            'locations': Locations.objects.all()
        }

        return render(request, 'dashboard/products/grn_entries.html', context=context)


def new_grn(request):
    context = {
        'nav': True,
        'page_title': 'New GRN',
        'locations': Locations.objects.all()
    }
    return render(request, 'dashboard/products/new_grn.html', context=context)


@login_required()
def profile(request):
    user = request.user
    if UserAddOns.objects.filter(user=user.pk).exists():
        pass
    else:
        use_ad_on = UserAddOns(user=User.objects.get(pk=user.pk),
                               company='',
                               app_version=VersionHistory.objects.get(version=settings.APP_VERSION),
                               profile_pic='static/assets/img/users/default.png')
        use_ad_on.save()
    context = {
        'user': user,
        'ad_on': UserAddOns.objects.get(user=user.pk),
    }
    return render(request, 'dashboard/profile/profile.html', context=context)


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required()
def ticket(request):
    context = {
        'nav': True,
        'ticket_count': TicketHd.objects.filter(owner=request.user).count(),
        'my_tickets': TicketHd.objects.filter(owner=request.user),
        'page': {
            'title': 'My Tickets'
        }
    }
    return render(request, 'dashboard/profile/tickets.html', context=context)


def all_tickets(request):
    context = {
        'nav': True,
        'ticket_count': 10,
        'my_tickets': TicketHd.objects.filter(status=0),
        'domain': tags.objects.all(),
        'page': {
            'title': 'All Tickets'
        }
    }
    return render(request, 'dashboard/profile/all-.html', context=context)


@login_required()
def make_ticket(request):
    user = request.user
    if request.method == 'POST':
        form = NewTicket(request.POST, request.FILES)
        files = UploadFIle(request.POST, request.FILES)

        if form.is_valid():
            try:
                form.save()
                # if files.is_valid():
                #     files.save()
                messages.success(request, "Ticket Added")


            except Exception as e:
                messages.success(request, f"Could Not Open Ticket {e}")

            return redirect('open-ticket')

        else:
            return HttpResponse(form)


def all_users(request):
    page['title'] = 'Users'
    context = {
        'nav': True,
        'page': page,
        'users': User.objects.all(),
        'ous': OrganizationalUnit.objects.all(),
        'unit_membs': UnitMembers.objects.all()
    }
    return render(request, 'dashboard/company/all-users.html', context=context)


def issues_branch(request, task, br):
    t_br = TaskBranchHD.objects.get(md_hash=br)
    task = TaskHD.objects.get(pk=t_br.task.pk)

    page['title'] = f"{task.title} / {t_br.br_name}"
    context = {
        'nav': True,
        'page': page,
        'branch': t_br,
        'taskHd': task,
        'branches': TaskBranchHD.objects.filter(task=TaskHD.objects.get(entry_uni=task.entry_uni))
    }
    return render(request, 'dashboard/task/branch.html', context=context)


def update_profile(request):
    if request.method == 'POST':
        form = request.POST

        # profile_pic = request.FILES['profile_pic']
        first_name = form['first_name']
        last_name = form['last_name']
        email = form['email']
        pk = form['pk']

        user = User.objects.get(pk=pk)
        ad_on = UserAddOns.objects.get(user=user)

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        about = form['about']
        company = form['company']
        position = form['position']
        country = form['country']
        phone = form['phone']

        ad_on.about = about
        ad_on.company = company
        ad_on.position = position
        ad_on.country = country
        ad_on.phone = phone

        try:
            ad_on.profile_pic = request.FILES['profile_pic']
        except Exception as e:
            pass

        user.save()
        ad_on.save()

        return redirect('profile')


def save_ou(request):
    if request.method == 'POST':
        form = NewOu(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                messages.success(request, e)
        else:
            messages.success(request, "Invalid Form")
    else:
        messages.success(request, "Invalid Request Method")

    return redirect('all-users')


def save_um(request):
    if request.method == 'POST':
        form = NewUM(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse(form)
    else:
        return HttpResponse("INVALID METHOD")

    return redirect('all-users')


@login_required()
def sms(request):
    page['title'] = "SMS Manager"
    context = {
        'nav': True,
        'page': page,
        'apis': SmsApi.objects.filter(status=1)

    }
    return render(request, 'dashboard/sms.html', context=context)


@login_required()
def new_sms_api(request):
    if request.method == 'POST':
        form = NewSMSApi(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse(form)
    else:
        return HttpResponse("INVALID METHOD")

    return redirect('sms')


@login_required()
def update_user_settings(request):
    if request.method == 'POST':
        form = request.POST
        pk = form['user']
        prim_noif = form['prim_noif']
        user = User.objects.get(pk=pk)

        if UserSettings.objects.filter(user=user).exists():
            # update
            setting = UserSettings.objects.get(user=user)
            setting.prim_noif = prim_noif
            setting.save()
        else:
            # insert
            UserSettings(user=user, prim_noif=prim_noif).save()

        return redirect('profile')


@login_required()
def bulk_sms(request):
    if request.method == 'POST':
        if request.method == 'POST':
            form = NewBulkSms(request.POST, request.FILES)
            if form.is_valid():
                try:
                    form.save()

                    # get last saved
                    last_bulk = BulkSms.objects.last()
                    file = last_bulk.file
                    import csv
                    success = 0
                    failed = 0
                    total = 0
                    with open(file.path, newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        header = next(reader)  # read the first row as the header
                        for row in reader:
                            # do something with each row
                            total = + 1
                            number = row[0]
                            if len(number) == 10:
                                print(f"{number} is valid")
                                Sms(api=last_bulk.api, message=last_bulk.message, to=number).save()
                                success = + 1
                                print(row)
                            else:
                                print(f"{number} is not a valid number")
                                failed = +1
                                print(row)
                    m = f"Total : {total}, Success : {success}, Failed : {failed} "
                    messages.success(request, m)
                    return redirect('sms')
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(form)
        else:
            return HttpResponse("INVALID METHOD")

        return redirect('sms')


def resetpasswordview(request, token):
    # get token
    resetoken = PasswordResetToken.objects.filter(token=token)
    if resetoken.count() == 1:
        # get details
        tken = PasswordResetToken.objects.get(token=token)
        user = tken.user

        context = {
            'user_pk': user.pk
        }
        return render(request, 'profile/resetpassword.html', context=context)

    return HttpResponse(token)


def resetpassword(request):
    if request.method == 'POST':
        form = request.POST
        password = form.get('password')
        compass = form.get('compass')
        user_pk = form.get('user')

        if password == compass:
            if is_valid_password(password):

                User = get_user_model()

                # Get the user object
                user = User.objects.get(pk=user_pk)

                # Set the new password
                user.set_password(password)

                # Save the user object to update the password
                user.save()

                # update reset password and set token valid to no
                restoken = PasswordResetToken.objects.get(user=user)
                adon = UserAddOns.objects.get(user=user)

                restoken.valid = 0
                adon.pword_reset = 0

                restoken.save()
                adon.save()

                return redirect('login')
            else:
                messages.success(request,
                                 "Password must be At least 8 characters long, Contains at least one uppercase letter, Contains at least one lowercase letter, Contains at least one digit, Contains at least one special character (e.g., !,@,#,$,%,&,*)")
                return redirect(request.META.get('HTTP_REFERER'))

        else:
            messages.success(request, "PASSWORD MUST MATCH")
            return redirect(request.META.get('HTTP_REFERER'))


def permissions(request,username):
    from django.contrib.auth.models import  ContentType
    # Fetch all model permissions for the auth app
    # app_label = 'auth'
    # content_type = ContentType.objects.get(app_label=app_label)
    perms = Permission.objects.all()

    context = {
        'perms': perms,
        'user': request.user,

    }
    return render(request,'dashboard/profile/permissions.html',context=context)


