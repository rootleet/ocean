#from bs4 import BeautifulSoup
import babel.numbers
# from unicodecsv import writer
import datetime
import hashlib
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.core import serializers
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from admin_panel.form import NewProduct
from admin_panel.models import *
from blog.models import *
from community.models import *


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



def is_logged_in(request):

    if request.user.is_active:

        pass
    else:
        print('hello')
        return redirect('login')


@login_required(login_url='/login/')
def index(request):
    # is_logged_in(request)
    return render(request, 'index.html')

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
        'providers': Providers.objects.all(),
        'notomem': NotificationGroups.objects.all()
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

# @login_required(login_url='/login/')
def view_task(request, task_id):
    context = {
        'taskHd': TaskHD.objects.get(entry_uni=task_id),
        'taskTran': TaskTrans.objects.filter(entry_uni=task_id),
        'domains':tags.objects.all()
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



        # new_domain_detail = tags.objects.get(id=new_domain)
        # old_domain_detail = tags.objects.get(id=curr_domain)

        task_tran = TaskTrans(entry_uni=task_uni,tran_title=f'Domain Switch From {curr_domain} To {new_domain}',tran_descr=reason,owner=request.user.pk)
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
            send_mail(subject, body, 'robolog', recipients, html_message=body,fail_silently=False)
            # update transactions
            Emails(sent_from='henrychase411@gmail.com',sent_to=to,subject=subject,body=body,email_type='task',ref=task_uni,status=1).save()
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


def emails(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all()
    context={
        'comm_tags': tags.objects.all(),
        'email_groups':EmailGroup.objects.all(),
        'emails':Emails.objects.all(),
        'email_address':NotificationGroups.objects.all()
    }
    return render(request, 'emails.html', context=context)


def add_notification_mem(request):
    if request.method == 'POST':
        form = request.POST
        full_name = form['full_name']
        email = form['email']
        phone = form['phone']
        emg = form['email_group']
        email_group = EmailGroup.objects.get(pk=emg)

        try:
            NotificationGroups(full_name=full_name,email_addr=email,mobile_number=phone,group=email_group).save()
            messages.error(request, f"{email} Added to {email_group.group_name}")
            return redirect('emails')
        except Exception as e:
            messages.error(request, f"There is an error adding email {e}")
            return redirect('emails')



def send_mail(request,task_id):
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
                email_address =  memeber.email_addr
                try:
                    group_email_addr += f" {email_address}"
                    email_address = memeber.email_addr
                    Emails(sent_from='Admin', sent_to=email_address, subject=subject, body=body, email_type='task',
                           ref=entry).save()
                except Exception as e:
                    print(f"Could Not sent on {e}")

            TaskTrans(entry_uni=entry,tran_title='Send Mail',tran_descr=f"Email has been send to {group_email_addr} with message {body}",owner=request.user.pk).save()
        # insert into notification
        messages.error(request, f"Email Sceduled to be sent to {group_email_addr}")
        return redirect('view_task',task_id=entry)


    else:
        context = {
            'entry': TaskHD.objects.get(entry_uni=task_id),
            'groups': EmailGroup.objects.all()
        }
        return render(request, 'send_task_mail.html', context=context)


def auto(request,tool):
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

                html_message = render_to_string('mail_template.html', {'body': body})
                plain_message = strip_tags(html_message)
                from_email = sent_from
                to = recipient
                try:


                    mail.send_mail(subject, body, from_email, [to], html_message=body)
                    # update transactions
                    q = Emails.objects.get(pk=email.pk)
                    q.status = 1
                    q.status_message = 'Email Sent'
                    q.save()

                    if email_type == 'task':
                        TaskTrans(entry_uni=email_ref,tran_title='Send Mail',tran_descr=body,owner=0)



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
                description = description,
                created_by = request.user.pk
            ).save()
            messages.error(request, f"Group Saved")
            return redirect('emails')
        except Exception as e:
            messages.error(request,f"Could Not Save Group {e}")
            return redirect('emails')


def inventory_tools(request):
    context = {
        'page_title':'Inventory Tools',
        'banks':BankAccounts.objects.filter(status=1),
        'suppliers':SuppMaster.objects.filter(status=1),
        'groups':ProductGroup.objects.filter(status=1),
        'packing':PackingMaster.objects.filter(status=1)
    }
    return render(request,'suppliers/inventory_tools.html',context = context)


def accounts(request):
    context = {
        'page_title': 'Accounts'
    }
    return render(request, 'accounts/acct_home.html', context=context)


def tax_master(request):
    # if posting a form
    if request.method == 'POST':
        form = request.POST
        function = form['function'] # function decides what to do
        if function == 'save_new_tax':
            #save new tax component
            tax_code = form['tax_code']
            tax_description = form['tax_description']
            rate = form['rate']
            try:

                if TaxMaster.objects.filter(tax_code=tax_code).count() == 0:
                    TaxMaster(tax_code=tax_code,tax_description=tax_description,tax_rate=rate,created_by=request.user.pk).save()
                    messages.success(request,'done%%New Tax Added')

                else:
                    messages.success(request, 'error%%Duplicate Tax Code')

                return render(request,'accounts/tax_master.htm')

            except Exception as e:

                messages.success(request,f'error%%{e}')
                return render(request,'accounts/tax_master.htm')

        else:
            # render tax master page
            return render(request,'accounts/tax_master.htm')

    else:
        # show all tax
        context = {
            'page_title':'Tax Master',
            'taxes':TaxMaster.objects.all().order_by('-pk')
        }
        return render(request,'accounts/tax_master.htm',context=context)


def bank_master(request):

    context={
        'page_title':'Bank Master',
        'accounts':BankAccounts.objects.all()
    }
    return render(request,'accounts/bank-master.html',context=context)


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
            SuppMaster(company=company,contact_person=contact_person,purch_group=purch_group,origin=origin,email=email,
                       mobile=mobile,city=city,street=street,taxable=taxable,bank_acct=BankAccounts.objects.get(pk=bank_acct),created_by=request.user.pk).save()
            messages.error(request,f"done%%Supplier {company} Added")
            return redirect('suppliers')
        except Exception as e:
            messages.error(request,f"error%%Could not save supplier {e}")
            return redirect('suppliers')

@login_required(login_url='/login/')
def products(request):
    if ProductMaster.objects.filter().count() < 1:
        # redirect to new products creation
        messages.error(request,f"done%%Inventory is empty, Create an item")
        return redirect('new-product')
    context = {
        'page_title':'Products Master | View','products':ProductMaster.objects.all()
    }
    return render(request,'products/view.html',context=context)

@login_required(login_url='/login/')
def new_products(request):
    is_logged_in(request)
    groups = ProductGroup.objects.filter(status=1)
    taxes = TaxMaster.objects.filter(status=1)
    packs = PackingMaster.objects.filter(status=1)
    supps = SuppMaster.objects.filter(status=1)


    if groups.count() < 1:
        messages.error(request,"done%%Create groups before you can add products")
        return redirect('inventory_tools')

    if supps.count() < 1:
        messages.error(request,"done%%Create or enable at least one supplier before you can add products")
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
        'page_title':'Products Master | New',
        'groups':groups,'taxes':taxes,'packs':packs,'supps':supps
    }
    return render(request,'products/new.html',context=context)

@login_required(login_url='/login/')
def save_group(request):
    if request.method == 'POST':
        form = request.POST
        group_name = form['group_name']

        try:
            ProductGroup(descr=group_name,created_by=request.user.pk).save()
            messages.error(request,f"New Group {group_name} Saved")
        except Exception as e:
            messages.error(request,f"Error saving new group {group_name} : {e}")

    return redirect('inventory_tools')

@login_required(login_url='/login/')
def save_sub_group(request):
    if request.method == 'POST':
        form = request.POST
        descr = form['descr']
        group = form['group']

        try:
            ProductGroupSub(group=ProductGroup.objects.get(pk=group),descr=descr,created_by=request.user.pk).save()
            messages.error(request,f"News subgroup added")
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
            PackingMaster(code=code,descr=description,created_by=request.user.pk).save()
            messages.error(request, f"News Packing {description} added")
        except Exception as e:
                messages.error(request, f"Failed adding Packing: {e}")

    return redirect('inventory_tools')


@login_required(login_url='/login/')
def suppliers(request):
    context = {
        'suppliers':SuppMaster.objects.all(),
        'accounts':BankAccounts.objects.all()
    }
    return render(request,'accounts/suppiers.html',context=context)


def save_new_product(request):
    form = NewProduct(request.POST,request.FILES)
    if form.is_valid():
        if ProductMaster.objects.filter(barcode=form.cleaned_data['barcode']).count() > 1:
            messages.error("Barcode Exist")
            return redirect('products')
        try:
            if form.save():
                # todo::validate packing for products creation
                obj=ProductMaster.objects.latest('id')
                purch_un = request.POST['purch_un']
                purch_qty = request.POST['purch_qty']
                ass_un = request.POST['ass_un']
                ass_qty = request.POST['ass_qty']

                ProductPacking(product=obj,packing_un=PackingMaster.objects.get(pk=purch_un),pack_qty=purch_qty,packing_type='P').save()
                ProductPacking(product=obj, packing_un=PackingMaster.objects.get(pk=ass_un), pack_qty=ass_qty, packing_type='P').save()

                messages.error('done%%Item Added')

            return redirect('products')

        except Exception as e:
            messages.error(request,f'error%%{e}')
            return HttpResponse(e)

    else:
        return HttpResponse(f'Invalid Form {form}')


def adjust_product_qty(request,p):
    if request.method == 'POST':
        form = request.POST
        pk = form['pk']
        tran_qty = form['qty']
        doc = form['type']
        doc_ref = "ADJUSTMENT"

        ProductTrans(doc=doc,doc_ref=doc_ref,tran_qty=tran_qty,product=ProductMaster.objects.get(pk=pk)).save()
        messages.error(request,'done%%Product Received')

        return redirect('products')

    else:
        product = ProductMaster.objects.get(pk=p)
        context = {
            'page_title': f'Received {product.descr}','product':product
        }
        return render(request,'products/adjust.html',context=context)