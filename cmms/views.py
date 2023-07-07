import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from ocean.settings import DB_SERVER, DB_NAME, DB_USER, DB_PORT, DB_PASSWORD
from django.contrib.auth import get_user_model
import pyodbc
from cmms.models import *
from decimal import Decimal
from django.contrib import messages

from cmms.extra import db


# Create your views here.
def base(request):
    return None


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
def stock_count(request):
    if StockCountHD.objects.filter(status=1).count() != 1:
        messages.error(request, 'NO OPEN STOCK COUNT.')
        return redirect('/cmms/stock/')
    context = {
        'nav': True,
    }
    return render(request, 'cmms/stock-take.html', context=context)


@csrf_exempt
def api(request):
    global header
    method = request.method
    response = {"status_code": "", "status": "", "message": ""}

    try:
        body = json.loads(request.body)
        module = body.get('module')
        data = body.get('data')

        if method == 'VIEW':
            if module == 'product':
                scope = data.get('range')
                barcode = data.get('barcode')

                if scope == 'single':
                    q = f"SELECT barcode,item_ref,item_des1 FROM product_master WHERE barcode = '{barcode}'"
                else:
                    q = "SELECT barcode,item_ref,item_des1  FROM product_master"

                server = f"{DB_SERVER},{DB_PORT}"
                database = DB_NAME
                username = DB_USER
                password = DB_PASSWORD
                driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
                connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
                connection = pyodbc.connect(connection_string)
                cursor = connection.cursor()

                cursor.execute(q)
                count = 0
                arr = []
                for part in cursor.fetchall():
                    count += 1
                    obj = {'barcode': part[0].strip(), 'item_ref': part[1].strip(), 'name': part[2].strip()}
                    arr.append(obj)

                resp = {'count': count, 'trans': arr}
                response['status_code'] = 200
                response['status'] = 'success'
                response['message'] = resp
                cursor.close()
                connection.close()

            elif module == 'stock':
                stage = data.get('stage')
                if stage == 'active':
                    # check for active
                    if StockCountHD.objects.filter(status=1).exists():
                        active = StockCountHD.objects.get(status=1)
                        trans = StockCountTrans.objects.filter(stock_count_hd=active).order_by('-pk')
                        arr = []
                        for tran in trans:
                            obj = {
                                'item_ref': tran.item_ref,
                                'barcode': tran.barcode,
                                'name': tran.name,
                                'quantity': tran.quantity,
                                'price': tran.sell_price,
                                'value': tran.quantity * tran.sell_price,
                                'owner': tran.owner
                            }
                            arr.append(obj)
                        response['message'] = {
                            'count': trans.count(), 'trans': arr
                        }
                        response['status_code'] = 200
                        response['status'] = 'success'
                    else:
                        response['message'] = 'NO DATA'
                        response['status_code'] = 404
                        response['status'] = 'error'

                if stage == 'export':
                    style = data.get('compare')
                    if style == 'final_compare':
                        # check if there is open stock
                        open_st = StockCountHD.objects.filter(status=1).count()
                        is_open = False
                        if open_st == 1:
                            pk = data.get('pk')
                            stock_hd = StockCountHD.objects.get(pk=pk)
                            as_of = data.get('as_of')
                            query = f"exec dbo.item_avail_loc_date N'{stock_hd.loc}',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'1%',N'%',N'%',N'%',N'family_id',1,N'SNEDA MOTORS',N'ITEM AVAILABILITY BY FAMILY \
                                As of ({as_of})',N'dd/mm/yyyy',N'#,###,###.00','{as_of}',N'1'"
                            cursor = db()
                            cursor.execute(query)
                            header = {
                                'location': stock_hd.loc,
                                'remark': stock_hd.remark
                            }
                            arr = []
                            not_arr = []
                            rows = cursor.fetchall()
                            for row in rows:

                                itemRref = row[6].strip()
                                name = row[7].strip()
                                group_code = row[4].strip()
                                print(group_code)
                                if group_code == '0109':

                                    av_qty = row[15].strip()
                                    # print()
                                    # print(f"RAW : {av_qty}")
                                    if len(av_qty) > 0:
                                        a_q = Decimal(av_qty.split('*')[0])
                                    else:
                                        a_q = 0.00

                                    # print(f"{av_qty} / {a_q}")
                                    # focus on filters
                                    item_q = cursor.execute(
                                        f"SELECT barcode,sell_price from product_master where item_ref = '{itemRref}'")
                                    item = item_q.fetchone()
                                    barcode = item[0]
                                    if item[1] is None:
                                        sell_price = 0.00
                                    else:
                                        sell_price = item[1]



                                    # check if there is item with ref

                                    counted = 0.00
                                    if StockCountTrans.objects.filter(item_ref=itemRref, stock_count_hd=stock_hd).exists():
                                        counted = StockCountTrans.objects.filter(item_ref=itemRref,
                                                                                 stock_count_hd=stock_hd).aggregate(
                                            total=Sum('quantity'))['total']

                                    diff_qty = Decimal(counted) - Decimal(a_q)
                                    obj = {
                                        'item_ref': itemRref,
                                        'barcode': barcode,
                                        'desription': name,
                                        'counted': counted,
                                        'av_qty': Decimal(str(a_q)),
                                        'qty_diff': diff_qty,
                                        'sell_price':sell_price,
                                        'diff_val': diff_qty * Decimal(sell_price),
                                    }
                                    if counted > 0:
                                        arr.append(obj)
                                    else:
                                        not_arr.append(obj)

                                response['message'] = {
                                    'header': header, 'trans': {'counted': arr, 'not_counted': not_arr}
                                }
                                response['status_code'] = 200
                                response['status'] = 'success'
                        else:
                            response['message'] = "NO OPEN STOCK"
                            response['status_code'] = 404
                            response['status'] = 'limit'

        elif method == 'PUT':
            if module == 'stock':
                stage = data.get('stage')
                if stage == 'hd':
                    loc = data.get('loc')
                    remark = data.get('remark')

                    # check if there is open hd
                    if StockCountHD.objects.filter(status=1).exists():
                        response['message'] = "There is an open stock take"
                        response['status_code'] = 505
                        response['status'] = 'WARNING'

                    else:
                        # open stock
                        StockCountHD(loc=loc, remark=remark).save()
                        response['status_code'] = 200
                        response['status'] = 'success'
                elif stage == 'tran':
                    item_ref = data.get('item_ref')
                    qty = data.get('qty')
                    myName = data.get('user')

                    username = myName
                    server = f"{DB_SERVER},{DB_PORT}"
                    database = DB_NAME
                    username = DB_USER
                    password = DB_PASSWORD
                    driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
                    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
                    connection = pyodbc.connect(connection_string)
                    cursor = connection.cursor()

                    query = f"select barcode,item_ref,item_des1,sell_price from product_master where item_ref = '{item_ref}'"
                    cursor.execute(query)

                    row = cursor.fetchone()
                    if row:
                        barcode = row[0].strip()
                        name = row[2].strip()
                        if row[3] is None:
                            sell_price = 0.00
                        else:
                            sell_price = row[3]
                        print(sell_price)
                        val = Decimal(qty) * Decimal(sell_price)
                        hd = StockCountHD.objects.get(status=1)
                        StockCountTrans(stock_count_hd=hd, item_ref=item_ref, barcode=barcode, name=name,
                                        sell_price=sell_price, quantity=qty, owner=myName, value=val).save()

                        response['status_code'] = 200
                        response['status'] = 'success'
                        response['message'] = f"ITEM {name} Added"
                        cursor.close()

                    else:
                        response['status_code'] = 404
                        response['status'] = 'error'
                        response['message'] = f"could not find item with ref {item_ref}"

        elif method == 'PATCH':
            if module == 'stock':
                stage = data.get('stage')
                task = data.get('task')
                if stage == 'hd':
                    if task == 'close':
                        opened = StockCountHD.objects.filter(status=1).last()
                        opened.status = 2
                        opened.save()
                        response = {'status': 200, 'status_code': 'success', 'message': "OPENED COUNT closed"}



    except json.JSONDecodeError as e:
        response["status_code"] = 400
        response["status"] = "Bad Request"
        response["message"] = f"Error decoding JSON: {e.msg}"

    return JsonResponse(response)
