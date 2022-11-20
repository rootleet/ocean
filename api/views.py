import hashlib
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from .ApiClass import *

from admin_panel.models import Notifications, AuthToken, Locations, SuppMaster, ProductMaster, ProductTrans, \
    ProductPacking
import json

from inventory.models import PoHd, PoTran, PriceCenter

# Create your views here.
api_response = {
    'status': 505,
    'response': 'PROCEDURE ERROR'
}


def console(str=''):
    print()
    print(str)
    print()


def get_notification(user):
    if User.objects.filter(pk=user).count() == 1:
        notifications = Notifications.objects.filter(owner=User.objects.get(pk=user))
        if notifications.count() > 0:
            api_response['status'] = 200
            read = Notifications.objects.filter(owner=User.objects.get(pk=user), read=1)
            my_notif = [

            ]
            not_read = Notifications.objects.filter(owner=User.objects.get(pk=user), read=0)
            my_notifications = Notifications.objects.filter(owner=User.objects.get(pk=user)).order_by('-pk')[:5]

            for my_n in my_notifications:
                # 1 = success, 2 = information, 3 = warning, 4 = errpr
                icon = ''
                n_type = my_n.type
                if n_type == 1:
                    icon = 'bi-check-circle text-success'
                elif n_type == 2:
                    icon = 'bi-info-circle text-info'
                elif n_type == 3:
                    icon = 'bi-exclamation-circle text-warning'
                else:
                    icon = 'bi-exclamation-circle text-danger'

                this_x = {
                    'title': my_n.title,
                    'type': my_n.type,
                    'descr': my_n.descr,
                    'status': my_n.read,
                    'icon': icon
                }
                my_notif.append(this_x)

            message = {
                'r_count': read.count(),
                'n_read': not_read.count(),
                'notifications': my_notif
            }
            api_response['response'] = message
        else:
            api_response['response'] = 'There is None'
        return JsonResponse(api_response, safe=False)
    else:
        return HttpResponse("USER NOT FOUND")


@csrf_exempt
def api_call(request, module, crud):
    global f_name
    response = {
        'status': 505,
        'message': "No Module "
    }
    try:
        api_body = json.loads(request.body)
    except Exception as e:
        pass

    if module == 'notif':
        user = api_body['user']
        return get_notification(user=user)

    elif module == 'auth':  # authentication model queried
        api_token = crud  # api access token

        token_filter = AuthToken.objects.filter(token=api_token)  # filter for token existence

        if token_filter.count() == 1:  # if there is token
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
                                   f"There is an error logging in, please check your credentials again or contact "
                                   f"Administrator")
                    return redirect('login')

            except Exception as e:
                messages.error(request, f"There was an error {e}")
                return redirect('login')

        else:
            return HttpResponse('INVALID TOKEN')

    # purchase order
    elif module == 'po':
        # save new po header
        if crud == 'newHd':
            data = api_body
            location = data['location']
            supplier = data['supplier']
            remarks = data['remarks']
            owner = User.objects.get(pk=data['owner'])
            taxable = data['taxable']

            response['status'] = 200
            response['message'] = data

            # save po hd
            try:
                PoHd(loc=Locations.objects.get(pk=location), supplier=SuppMaster.objects.get(pk=supplier),
                     remark=remarks, created_by=owner, taxable=taxable, approved_date='1999-01-01',approved_time='00:00:00').save()
                response['message'] = PoHd.objects.all().last().pk
                response['status'] = 200

            except Exception as e:
                response['status'] = 505
                response['message'] = str(e)

        # save new po transaction
        elif crud == 'newTran':
            data = api_body
            entry_no = data['entry_no']

            line = data['line']

            barcode = data['barcode']
            if ProductMaster.objects.filter(barcode=barcode).exists():

                product = ProductMaster.objects.get(barcode=barcode)

                packing = data['packing']
                qty = data['qty']
                total_qty = data['total_qty']
                un_cost = data['un_cost']
                tot_cost = data['tot_cost']

                try:
                    PoTran(entry_no=PoHd.objects.get(pk=entry_no), line=line, product=product, packing=packing,
                           qty=qty, total_qty=total_qty, un_cost=un_cost, tot_cost=tot_cost).save()
                    response['status'] = 200
                    response['message'] = "Data Saved"

                except Exception as e:
                    response['status'] = 505
                    response['message'] = e

            else:
                response['message'] = "Product Does Not Exist"

        # get po transaction
        elif crud == 'get':
            data = api_body
            entry = data['entry']

            meg = {}

            if PoHd.objects.filter(pk=entry).exists():
                # if po exist
                hd = PoHd.objects.get(pk=entry)

                header = {
                    'header': {
                        'entry_no': f"PO{hd.loc.code}{hd.pk}",
                        'loc_code': hd.loc.code,
                        'loc_descr': hd.loc.descr,
                        'supp_pk': hd.supplier.pk,
                        'supp_descr': hd.supplier.company,
                        'remark': hd.remark,
                        'entry_date': hd.created_on,
                        'owner': hd.created_by.first_name,
                        'pk': hd.pk
                    }
                }

                # get trans
                trans = {
                    'trans': {
                        'count': 0,
                        'transactions': []
                    }
                }

                if PoTran.objects.filter(entry_no=entry).exists():

                    transactions = PoTran.objects.filter(entry_no=entry)
                    trans['trans']['count'] = transactions.count()

                    for transaction in transactions:
                        this_trans = {
                            'line': transaction.line,
                            'product_descr': transaction.product.descr,
                            'product_barcode': transaction.product.barcode,
                            'packing': transaction.packing,
                            'qty': transaction.qty,
                            'total_qty': transaction.total_qty,
                            'un_cost': transaction.un_cost,
                            'tot_cost': transaction.tot_cost
                        }
                        trans['trans']['transactions'].append(this_trans)

                else:
                    pass

                transactions = PoTran

                # navigators
                next_count = PoHd.objects.filter(pk__gt=hd.pk).count()
                prev_count = PoHd.objects.filter(pk__lt=hd.pk).count()

                if prev_count > 0:
                    prev = PoHd.objects.all().filter(pk__lt=hd.pk)
                    for x in prev:
                        prev_p = str(x.pk)
                else:
                    prev_p = 0

                if next_count > 0:
                    next_po = PoHd.objects.all().filter(pk__gt=hd.pk)[:1]
                    for y in next_po:
                        next_p = str(y.pk)
                else:
                    next_p = 0

                nav = {
                    'nav': {
                        'status': hd.status,
                        'next_count': next_count,
                        'next_id': next_p,
                        'prev_count': prev_count,
                        'prev_id': prev_p
                    }
                }

                cost = {
                    'cost': {
                        'taxable': hd.taxable,
                        'taxable_amt': PoTran.objects.filter(entry_no=hd.pk).aggregate(Sum('tot_cost'))[
                            'tot_cost__sum'],
                        'tax_nhis': 0.00,
                        'tax_gfund': 0.00,
                        'tax_covid': 0.00,
                        'tax_vat': 0.00,
                        'tax_amt': 0.00
                    }
                }

                if cost['cost']['taxable'] == 1:
                    # calculate taxes
                    taxable_amt = cost['cost']['taxable_amt']
                    cost['cost']['tax_covid'] = round(Decimal(taxable_amt) * Decimal(0.001), 2)
                    cost['cost']['tax_nhis'] = round(Decimal(taxable_amt) * Decimal(0.025), 2)
                    cost['cost']['tax_gfund'] = round(Decimal(taxable_amt) * Decimal(0.025), 2)

                    levies = cost['cost']['tax_covid'] + cost['cost']['tax_nhis'] + cost['cost']['tax_gfund']
                    new_tot_amt = taxable_amt + levies

                    cost['cost']['tax_vat'] = round(Decimal(new_tot_amt) * Decimal(0.125), 2)
                    cost['cost']['tax_amt'] = round(levies + cost['cost']['tax_vat'], 2)

                meg.update(header)
                meg.update(trans)
                meg.update(nav)
                meg.update(cost)

                response['status'] = 200
                response['message'] = meg

            else:
                # if no po, return 404 and response message
                response['status'] = 404
                response['message'] = "Po Entry Not Found"

    # products master
    elif module == 'product':
        if crud == 'get_product':
            barcode = api_body['barcode']

            if ProductMaster.objects.filter(barcode=barcode).exists():
                response['status'] = 200
                pd = ProductMaster.objects.get(barcode=barcode)
                stock = ProductTrans.objects.filter(product=pd.pk).aggregate(Sum('tran_qty'))['tran_qty__sum']
                if PriceCenter.objects.filter(product=pd.pk, price_type=0).exists():
                    cost_price = PriceCenter.objects.get(product=pd.pk, price_type=0).price
                else:
                    cost_price = 0.00
                if PriceCenter.objects.filter(product=pd.pk, price_type=1).exists():
                    issue_price = PriceCenter.objects.get(product=pd.pk, price_type=1).price
                else:
                    issue_price = 0.00

                prod_pack = []

                if ProductPacking.objects.filter(product=pd).exists():
                    pack = ProductPacking.objects.filter(product=pd)
                    for p in pack:
                        this_p = {
                            'pack_type': p.packing_type,
                            'pack_qty': p.pack_qty,
                            'pack_code': p.packing_un.code,
                            'pack_descr': p.packing_un.descr
                        }
                        prod_pack.append(this_p)
                        print(this_p)

                prod_grp = {
                    'group': pd.group.descr, 'sub_group': pd.sub_group.descr,
                }

                product = {
                    # group details
                    'group': prod_grp,

                    # tax details
                    'tax': {'tax_code': pd.tax.tax_code, 'tax_descr': pd.tax.tax_description,
                            'tax_rate': pd.tax.tax_rate, },

                    # supplier details
                    'supplier': {'sup_company': pd.supplier.company, 'sup_pk': pd.supplier.pk, },

                    # product details
                    'prod_details': {'barcode': pd.barcode, 'prod_descr': pd.descr, 'prod_sht_descr': pd.shrt_descr,
                                     'prod_img': pd.prod_img.url, 'pk': pd.pk, },

                    # others
                    'others': {'stock': stock, 'cost_price': cost_price, 'issue_price': issue_price, },

                    # packing
                    'prod_pack': prod_pack

                }
                response['message'] = product

            else:
                response['status'] = 505
                response['message'] = "Product Does Not Exist"

    # general
    elif module == 'general':
        if crud == 'print':
            doc = api_body['doc']
            entry_no = api_body['entry_no']

            if doc == 'po':
                res = GetPo(entry_no)
                status = res['status']
                message = res['message']
                trans = message['trans']['transactions']
                header = message['header']
                prices = message['cost']
                p_status = message['p_status']

                tax = 'NO'
                if prices['taxable'] == 1:
                    tax = "YES"

                if status == 200:

                    pdf = FPDF('L', 'mm', 'A4')
                    pdf.add_page()
                    pdf.set_margin(10)
                    # header

                    pdf.set_font('Arial', 'BU', 25)
                    pdf.cell(280, 5, "PURCHASE ORDER", 0, 1, 'C')
                    pdf.ln(10)
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(30, 5, "Entry : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(150, 5, header['entry_no'], 0, 0, 'L')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(35, 5, "Date : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(30, 5, str(header['entry_date']), 0, 1, 'L')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(30, 5, "Created By : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(150, 5, header['owner'], 0, 0, 'L')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(35, 5, "Location : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(30, 5, header['loc_descr'], 0, 1, 'L')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(30, 5, "Supplier : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(150, 5, header['supp_descr'], 0, 0, 'L')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(35, 5, "Taxable : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(30, 5, tax, 0, 1, 'L')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(30, 5, "Remarks : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(30, 5, header['remark'], 0, 0, 'L')

                    pdf.cell(120, 5, '', 0, 0, 'L')
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(35, 5, "Inv Amount : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(30, 5, str(prices['taxable_amt']), 0, 1, 'L')

                    pdf.cell(180, 5, '', 0, 0, 'L')
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(35, 5, "Tax Amount : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(30, 5, str(prices['tax_amt']), 0, 1, 'L')

                    pdf.cell(180, 5, '', 0, 0, 'L')
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(35, 5, "Total Amount : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(30, 5, str(Decimal(prices['tax_amt']) + Decimal(prices['taxable_amt'])), 0, 1, 'L')

                    pdf.ln(10)

                    pdf.set_font('Arial', 'B', 10)
                    # table head
                    pdf.cell(10, 5, "SN", 1, 0, 'L')
                    pdf.cell(60, 5, "BARCODE", 1, 0, 'L')
                    pdf.cell(70, 5, "DESCRIPTION", 1, 0, 'L')
                    pdf.cell(50, 5, "PACKING", 1, 0, 'L')
                    pdf.cell(20, 5, "QTY", 1, 0, 'L')
                    pdf.cell(30, 5, "UNIT COST", 1, 0, 'L')
                    pdf.cell(40, 5, "TOTAL COST", 1, 1, 'L')

                    pdf.set_font('Arial', '', 8)
                    for transaction in trans:
                        pdf.cell(10, 5, f"{transaction['line']}", 1, 0, 'L')
                        pdf.cell(60, 5, f"{transaction['product_barcode']}", 1, 0, 'L')
                        pdf.cell(70, 5, f"{transaction['product_descr']}", 1, 0, 'L')
                        pdf.cell(50, 5, f"{transaction['packing']}", 1, 0, 'L')
                        pdf.cell(20, 5, f"{transaction['qty']}", 1, 0, 'L')
                        pdf.cell(30, 5, f"{transaction['un_cost']}", 1, 0, 'L')
                        pdf.cell(40, 5, f"{transaction['tot_cost']}", 1, 1, 'L')

                    # auth
                    pdf.ln(20)
                    pdf.set_left_margin(55)
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(40, 10, f"{header['owner']}", 1, 0, 'C')

                    pdf.set_left_margin(205)
                    pdf.cell(40, 10, f"{p_status['approved_by']}", 1, 1, 'C')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_left_margin(55)
                    pdf.cell(40, 10, f"Prepared By", 0, 0, 'C')

                    pdf.set_left_margin(205)
                    pdf.cell(40, 10, f"Approved By", 0, 1, 'C')

                    md_mix = f"{status}{message['header']['entry_no']}"
                    hash_object = hashlib.md5(md_mix.encode())
                    f_name = hash_object.hexdigest()
                    f_name = header['entry_no']

                    pdf.output(f'static/general/docs/{f_name}.pdf', 'F')

                    resp = {
                        'status': 200,
                        'file': f'/static/general/docs/{f_name}.pdf'
                    }

                else:
                    resp = res
                return JsonResponse(resp, safe=False)

    return JsonResponse(response, safe=False)


def index(request):
    return HttpResponse("NO OPRION")
