from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from admin_panel.models import Locations, SmsApi, Sms
from cmms.extra import db
from retail.forms import NewClerk
from retail.models import Clerk


# Create your views here.
def base(request):
    context = {
        'nav': True
    }
    return render(request, 'retail/index.html', context=context)


def clerks(request):
    import random

    # Define the range for the random numbers (between 1000 and 9999)
    min_num = 1000
    max_num = 9999

    # Generate four random integers in the thousands range
    code = random.randint(min_num, max_num)
    pword = random.randint(min_num, max_num)

    context = {
        'nav': True,
        'locs': Locations.objects.all(),
        'clerks': Clerk.objects.all(),
        'code':code,
        'pwrod':pword
    }
    return render(request, 'retail/clerks.html', context=context)


def save_clerk(request):
    if request.method == 'POST':
        form = NewClerk(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                phone = form.cleaned_data['phone']
                code = form.cleaned_data['code']
                password = form.cleaned_data['pword']
                sms_api = SmsApi.objects.get(is_default=1)
                message = f"An Account has been created for you in Sneda Shopping Center POS. Below are your credentials \nCODE : {code}\nPassword : {password}"
                Sms(api=sms_api,to=phone,message=message).save()
                messages.success(request, "CLERK ADDED")
            except Exception as e:
                messages.error(request, f"EXCEPTION OCCURRED : {e}")
        else:
            messages.error(request, f"COULD NOT SAVE CLERK {form.errors}")


    else:
        messages.error(request, f"INVALID METHOD {request.method}")

    return redirect('clerks')


def sync_clerks(request, fr):
    try:
        if fr == 'locations':
            # sync from locations
            locations = Locations.objects.all()

            for location in locations:
                ip = location.ip_address
                database = location.db
                db_us = location.db_user
                db_pw = location.db_password

                cursor = db(ip, 1433, database, db_us, db_pw)

                # get all clerks
                cursor.execute("SELECT clrk_code,clrk_name,clrk_pwd,clrk_type FROM clerk_mast")
                for clerk in cursor.fetchall():
                    # get detail
                    clrk_code = clerk[0]
                    clrk_name = clerk[1]
                    clrk_pwd = clerk[2]
                    clrk_type = clerk[3]

                    # split name
                    name = clrk_name.split(',')
                    if len(name) > 1:
                        first_name = name[0]
                        last_name = name[1]
                    else:
                        first_name = clrk_name
                        last_name = ""

                    # insert into clerks
                    if Clerk.objects.filter(code=clrk_code).count() == 0:
                        Clerk(first_name=first_name, last_name=last_name, pword=clrk_pwd, code=clrk_code,
                              phone=clrk_code, location=location, flag_dwn=0, flag_disable=0).save()

                cursor.close()

        elif fr == 'ocean':
            clks = Clerk.objects.filter(flag_dwn=1)
            for clk in clks:
                pk = clk.pk
                name = f"{clk.first_name} {clk.last_name}"
                code = clk.code
                pword = clk.pword
                location = clk.location
                ip = location.ip_address
                database = location.db
                db_us = location.db_user
                db_pw = location.db_password

                cursor = db(ip, 1433, database, db_us, db_pw)

                # send
                try:
                    cursor.execute(
                        f"insert into clerk_mast (clrk_code,clrk_name,clrk_pwd,clrk_type) values ('{code}','{name}','{pword}',0)")
                    cursor.commit()

                except Exception as e:
                    pass

                cursor.close()
                # update clerk download flag
                new_c = Clerk.objects.get(pk=pk)
                new_c.flag_dwn = 0
                new_c.save()


        return HttpResponse('SYNC COMPLETED')
    except Exception as e:
        return HttpResponse(e)
