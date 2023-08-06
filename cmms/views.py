import csv
import json
import traceback
from datetime import date
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from cmms.forms import NewSalesCustomer, NewSaleTransactions
from ocean.settings import DB_SERVER, DB_NAME, DB_USER, DB_PORT, DB_PASSWORD
from django.contrib.auth import get_user_model
import pyodbc
from cmms.models import *
from decimal import Decimal
from django.contrib import messages

from cmms.extra import db, DB_CURSOR


# Create your views here.
def base(request):
    page = {
        'nav': True,
        'title': "CMMS"
    }

    context = {
        'page': page,
        'nav': True,
        'searchButton': ''
    }
    return render(request, 'cmms/cmms-landing.html', context=context)


@login_required(login_url='/login/')
def carjobs(request):
    page = {
        'nav': True,
        'title': "Car Jobs"
    }

    context = {
        'page': page,
        'nav': True,
        'searchButton': 'carJob'
    }
    messages.info(request, "You can now view all data but limited to 100 records")
    return render(request, 'cmms/car-jobs.html', context=context)


@login_required()
def tools(request):
    context = {
        'nav': True
    }
    return render(request, 'cmms/tools.html', context=context)


@login_required()
def stock(request):
    opened = False
    if StockCountHD.objects.filter(status=1).count() == 1:
        opened = True
    return render(request, 'cmms/stock.html',
                  context={'nav': True, 'stocks': StockCountHD.objects.all(), 'open': opened})


@login_required()
def new_frozen(request):
    context = {'nav': True}
    return render(request, 'cmms/new_stock.html', context=context)


def new_count(request, frozen):
    context = {'nav': True}
    return render(request, 'cmms/count.html', context=context)


@login_required()
def forezen(request):
    froze = StockFreezeHd.objects.all()
    if froze.count() < 1:
        messages.warning(request, "PLEASE FREEZE NEW STOCK")
        return redirect('/cmms/stock/frozen/new/')
    else:
        f_pk = froze.last().pk
    context = {'nav': True, 'f_pk': f_pk}
    return render(request, 'cmms/frozen.html', context=context)


@login_required()
def new_stock_count(request):
    # if StockCountHD.objects.filter(status=1).count() != 1:
    #     messages.error(request, 'NO OPEN STOCK COUNT.')
    #     return redirect('/cmms/stock/')
    context = {
        'nav': True,
        'page': {
            'title': "STOCK COUNT"
        }
    }
    return render(request, 'cmms/count.html', context=context)


@login_required()
def view_stock_count(request):
    if StockCountHD.objects.filter(status=1).count() < 1:
        messages.error(request, 'NO OPEN STOCK COUNT.')
        return redirect('/cmms/stock/new/')
    context = {
        'nav': True,
        'page': {
            'title': "STOCK COUNT VIEW"
        },
        'c_pk': StockCountHD.objects.filter(status=1).last().pk
    }
    return render(request, 'cmms/count_view.html', context=context)


@login_required()
def edit_stock_count(request, pk):
    if StockCountHD.objects.filter(pk=pk).count() < 1:
        messages.error(request, 'NO OPEN STOCK COUNT.')
        return redirect('/cmms/stock/new/')
    context = {
        'nav': True,
        'page': {
            'title': "STOCK COUNT VIEW"
        },
        'c_pk': pk
    }
    return render(request, 'cmms/count_edit.html', context=context)


@login_required()
def compare(request, pk, as_of, group):
    # get counts
    hd = StockCountHD.objects.get(pk=pk)
    wrong_entries = StockCountTrans.objects.filter(stock_count_hd=hd, issue__in='wr_entry').count()
    sys_error = StockCountTrans.objects.filter(stock_count_hd=hd, issue__in='sys_error').count()
    lost = StockCountTrans.objects.filter(stock_count_hd=hd, issue__in='lost').count()
    unknown = StockCountTrans.objects.filter(stock_count_hd=hd, issue__in='unknown').count()
    return render(request, 'cmms/compare.html', context={
        'nav': True,
        'as_of': as_of,
        'pk': pk,
        'group': group,
        'wrong_entries': wrong_entries,
        'sys_error': sys_error,
        'lost': lost,
        'unknown': unknown,

    })


@login_required()
def customer_sales(request):
    context = {
        'nav': True,
        'page': {
            'title': "SALES CUSTOMERS"
        },
        'customers': SalesCustomers.objects.all().order_by('-pk')
    }
    return render(request, 'cmms/sales-customer.html', context=context)


@login_required()
def new_sales_customer(request):
    context = {
        'nav': True,
        'page': {
            'title': "NEW SALES CUSTOMER"
        }
    }
    return render(request, 'cmms/new-sales-customer.html', context=context)


@login_required()
def save_sales_customer(request):
    if request.method == 'POST':
        form = NewSalesCustomer(request.POST)
        mobile = request.POST['mobile']
        email = request.POST['email']
        if SalesCustomers.objects.filter(mobile=mobile).exists():
            messages.error(request, f"Customer exist with number {mobile}")
        elif SalesCustomers.objects.filter(email=email).exists():
            messages.error(request, f"Customer exist with number {mobile}")
        elif form.is_valid():
            try:
                form.save()
                messages.success(request, "CUSTOMER ADDED")
            except IntegrityError:
                messages.error(request, "CUSTOMER ALREADY EXISTS")
            except Exception as e:
                messages.error(request, str(e))
        else:
            # return HttpResponse(form)
            messages.error(request, "FORM IS INVALID")
    else:
        messages.error(request, "WRONG REQUEST METHOD")

    return redirect('customer_sales')


def sales_customer_transactions(request, customer):
    context = {
        'page': {
            'title': ""
        },
        'cust': SalesCustomers.objects.get(pk=customer)
    }
    return render(request, 'cmms/sales_transactions.html', context=context)

@login_required()
def save_sales_transaction(request):
    if request.method == 'POST':
        form = NewSaleTransactions(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.error(request, "TRANSACTION SAVED")

            except Exception as e:
                messages.error(request, str(e))
            # To return to the previous page
            previous_page = request.META.get('HTTP_REFERER')
            return redirect(previous_page)
        else:
            messages.error(request, "FORM IS INVALID")
    else:
        messages.error(request, "WRONG REQUEST METHOD")

    return redirect('customer_sales')

@login_required()
def service_customers(request):
    context = {
        'nav': True,
        'page': {

            'title': "SERVICE CUSTOMERS"
        }
    }
    return render(request, 'cmms/service/customers.html', context=context)

@login_required()
def sales_deal(request,customer):
    # validate customer
    if SalesCustomers.objects.filter(url=customer).count() == 1:
        cust = SalesCustomers.objects.get(url=customer)
        context = {
            'nav': True,
            'page': {
                'title': f"{cust.company} / DEALS"
            },
            'customer':cust
        }

        return render(request,'cmms/sales-cust.html',context=context)
    else:
        messages.error(request,f"NO CUSTOMER WITH URL {customer}")
        return redirect('customer_sales')

