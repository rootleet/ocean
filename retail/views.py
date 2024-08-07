from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from admin_panel.models import Locations, SmsApi, Sms
from cmms.extra import db
from retail.forms import NewClerk
from retail.models import Clerk, BoltItems, BoltGroups, Products, RecipeProduct


@login_required()
def base(request):
    context = {
        'nav': True
    }
    return render(request, 'retail/index.html', context=context)


@login_required()
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
        'code': code,
        'pwrod': pword
    }
    return render(request, 'retail/clerks.html', context=context)


@login_required()
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
                Sms(api=sms_api, to=phone, message=message).save()
                messages.success(request, "CLERK ADDED")
            except Exception as e:
                messages.error(request, f"EXCEPTION OCCURRED : {e}")
        else:
            messages.error(request, f"COULD NOT SAVE CLERK {form.errors}")


    else:
        messages.error(request, f"INVALID METHOD {request.method}")

    return redirect('clerks')


@login_required()
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


@login_required()
def bolt_products(request):
    context = {
        'nav': True,
        'page': {
            'title': "Bolt Products"
        },
        'items': BoltItems.objects.all()
    }
    return render(request, 'retail/bolt-products.html', context=context)


@login_required()
def bolt_groups(request):
    context = {
        'nav': True,
        'page': {
            'title': "Bolt Categories"
        },
        'groups': BoltGroups.objects.all()
    }
    return render(request, 'retail/bolt-groups.html', context=context)

from django.core.paginator import Paginator, Page
class CustomPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = 500

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.batch_size
        top = bottom + self.batch_size
        if top > self.count:
            top = self.count
        return Page(self.object_list[bottom:top], number, self)

def has_next_page(current_page, paginator):
    return current_page.has_next()

@login_required()
def products(request,page=1):
    if Products.objects.all().count() > 500:

        page_size = 500
        ct = page * page_size
        lt = abs(page_size - ct)


        all_products = Products.objects.all()[:ct]
        last_500_products = list(all_products)[lt:]

        last_pk = last_500_products[-1].pk
        first_pk = last_500_products[0].pk

        print(first_pk,last_pk)

        next_page = False
        if Products.objects.filter(pk__gt=last_pk):
            next_page = True
        previous_page = False
        if Products.objects.filter(pk__lt=first_pk):
            previous_page = True
    else:
        last_500_products = Products.objects.all()
        next_page = False
        previous_page = False

    # reset all products
    last_500_products = Products.objects.all()
        

    context = {
        'nav': True,
        'page': {
            'title': "Product Master"
        },
        'items': last_500_products,
        'is_next':next_page,
        'next':page + 1,
        'is_previous':previous_page,
        'preious':page - 1
    }
    return render(request, 'retail/products.html', context=context)


@login_required()
def recipe(request):
    context = {
        'nav': True,
        'closed': RecipeProduct.objects.filter(is_open=False),
        'stat': {
            'done': RecipeProduct.objects.filter(is_open=False).count(),
            'pending': RecipeProduct.objects.filter(is_open=True).count(),
        }

    }
    return render(request, 'retail/recipe/landing.html', context=context)


@login_required()
def recipe_group(request, group_id):
    context = {
        'nav': True,
        'group_id': group_id
    }
    return render(request, 'retail/recipe/recipe_group.html', context=context)


@login_required()
@csrf_exempt
def upload_item_image(request):
    if request.method == 'POST':
        product_key = request.POST['prod_pk']
        image = request.FILES['prod_image']

        product = RecipeProduct.objects.get(pk=product_key)
        grp_pk = product.group.pk
        product.image = image
        product.save()
        messages.success(request, "Image Uploaded")

    return redirect('recipe_group', grp_pk)

@login_required()
def recipe_card(request):
    context = {
        'nav': True,
        'last_pk':RecipeProduct.objects.all().last().pk
    }
    return render(request, 'retail/recipe/card.html', context=context)

@login_required()
def stock(request):
    context = {
        'nav':True,
    }

    return render(request,'retail/stock/frozen.html',context=context)

@login_required()
def stock_monitor(request):
    context = {
        'nav': True,
    }

    return render(request, 'retail/stock/minotoring.html', context=context)