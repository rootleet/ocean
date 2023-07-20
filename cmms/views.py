import json
import traceback
from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
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
    messages.info(request, "Please not, you can only filter data as of 1st April 2023 and forward")
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
def new_stock_count(request):
    context = {'nav': True}
    return render(request, 'cmms/new_stock.html', context=context)


@login_required()
def forezen(request):
    froze = StockFreezeHd.objects.all()
    if froze.count() < 1:
        messages.warning(request, "PLEASE FREEZE NEW STOCK")
        return redirect('/cmms/stock/')
    else:
        f_pk = froze.last().pk
    context = {'nav': True, 'f_pk': f_pk}
    return render(request, 'cmms/frozen.html', context=context)


@login_required()
def stock_count(request):
    if StockCountHD.objects.filter(status=1).count() != 1:
        messages.error(request, 'NO OPEN STOCK COUNT.')
        return redirect('/cmms/stock/')
    context = {
        'nav': True,
    }
    return render(request, 'cmms/stock-take.html', context=context)


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
            try:
                if module == 'product':
                    scope = data.get('range')
                    item_uni = data.get('item_uni')
                    db_col = data.get('db_col') or 'barcode'

                    if scope == 'single':
                        q = f"SELECT barcode,item_ref,item_des1 FROM product_master WHERE {db_col} = '{item_uni}'"
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

                elif module == 'groups':
                    cursor = db()
                    query = "select Group_code,group_des from group_master order by group_des"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    arr = []
                    grp_counts = 0
                    for row in rows:
                        grp_counts += 1
                        group_code = row[0].strip()
                        group_name = row[1].strip()
                        arr.append({'code': group_code, 'name': group_name})

                    response['message'] = {
                        'counts': grp_counts, 'groups': arr
                    }
                    response['status_code'] = 200
                    response['status'] = 'success'


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
                                    'owner': tran.owner,
                                    'comment': tran.comment
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

                    elif stage == 'export':
                        style = data.get('compare')
                        if style == 'final_compare':
                            doc = data.get('doc')
                            tot_phy = Decimal(0.00)
                            tot_sys = Decimal(0.00)
                            tot_qdif = Decimal(0.00)
                            tot_vdif = Decimal(0.00)
                            if doc == 'excel':
                                import openpyxl
                                workbook = openpyxl.Workbook()
                                sheet = workbook.active
                                # make sheet head
                                sheet[f'A1'] = "ITEM REFERENCE"
                                sheet[f'B1'] = "BARCODED"
                                sheet[f'C1'] = "DESCRIPTION"
                                sheet[f'D1'] = "PHYSICAL QUANTITY"
                                sheet[f'E1'] = "SYSTEM QUANTITY"
                                sheet[f'F1'] = "QUANTITY DIFFERENCE"
                                sheet[f'G1'] = "SELLING PRICE"
                                sheet[f'H1'] = "VALUE DIFFERENCE"
                                sheet[f'I1'] = "COMMENT"

                            # check if there is open stock
                            pk = data.get('pk')
                            open_st = StockCountHD.objects.filter(pk=pk).count()
                            is_open = False
                            if open_st == 1:

                                stock_hd = StockCountHD.objects.get(pk=pk)
                                group = data.get('group')
                                cursor = db()
                                # get group from database
                                g_q = f"select group_des from group_master where group_code = '{group}'"
                                cursor.execute(g_q)
                                g_name = cursor.fetchone()[0]
                                as_of = data.get('as_of')
                                query = f"exec dbo.item_avail_loc_date N'{stock_hd.loc}',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'%',N'1%',N'%',N'%',N'%',N'family_id',1,N'SNEDA MOTORS',N'ITEM AVAILABILITY BY FAMILY \
                                    As of ({as_of})',N'dd/mm/yyyy',N'#,###,###.00','{as_of}',N'1'"

                                cursor.execute(query)
                                header = {
                                    'location': stock_hd.loc,
                                    'remark': stock_hd.remark,
                                    'group': g_name.strip()
                                }
                                arr = []
                                not_arr = []
                                entries = {
                                    'wr_entry': 0,
                                    'lost': 0,
                                    'sys_error': 0,
                                    'unknown': 0,
                                    'not_counted': 0
                                }
                                values = {
                                    'wr_entry': 0,
                                    'lost': 0,
                                    'sys_error': 0,
                                    'unknown': 0,
                                    'not_counted': 0
                                }
                                row_c = 2
                                rows = cursor.fetchall()
                                for row in rows:

                                    itemRref = row[6].strip()
                                    name = row[7].strip()
                                    group_code = row[4].strip()
                                    group_name = row[5].strip()

                                    if group_code == group:

                                        row_c += 1
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
                                        barcode = item[0].strip()
                                        if item[1] is None:
                                            sell_price = 0.00
                                        else:
                                            sell_price = item[1]

                                        # check if there is item with ref

                                        counted = 0.00
                                        el_pk = 0
                                        comment = 'not counted'
                                        if StockCountTrans.objects.filter(item_ref=itemRref,
                                                                          stock_count_hd=stock_hd).exists():
                                            counted = StockCountTrans.objects.filter(item_ref=itemRref,
                                                                                     stock_count_hd=stock_hd).aggregate(
                                                total=Sum('quantity'))['total']
                                            oc_item = StockCountTrans.objects.filter(item_ref=itemRref,
                                                                                     stock_count_hd=stock_hd).last()
                                            comment = oc_item.comment
                                            el_pk = oc_item.pk

                                        diff_qty = Decimal(counted) - Decimal(a_q)
                                        obj = {
                                            'item_ref': itemRref,
                                            'barcode': barcode,
                                            'desription': name,
                                            'counted': counted,
                                            'av_qty': Decimal(str(a_q)),
                                            'qty_diff': diff_qty,
                                            'sell_price': sell_price,
                                            'diff_val': diff_qty * Decimal(sell_price),
                                            'comment': comment,
                                            'pk': el_pk
                                        }

                                        if doc == 'preview':
                                            if counted > 0:
                                                arr.append(obj)
                                                if entries.get(comment) is not None:
                                                    entries[comment] += 1
                                                    values[comment] += diff_qty * Decimal(sell_price)
                                            else:
                                                not_arr.append(obj)
                                                entries['not_counted'] += 1
                                                values['not_counted'] += diff_qty * Decimal(sell_price)


                                        elif doc == 'excel':

                                            sheet[f'A{row_c}'] = itemRref
                                            sheet[f'B{row_c}'] = barcode
                                            sheet[f'C{row_c}'] = name
                                            sheet[f'D{row_c}'] = counted
                                            sheet[f'E{row_c}'] = Decimal(str(a_q))
                                            sheet[f'F{row_c}'] = diff_qty
                                            sheet[f'G{row_c}'] = sell_price
                                            sheet[f'H{row_c}'] = diff_qty * Decimal(sell_price)
                                            sheet[f'I{row_c}'] = comment

                                            tot_phy += Decimal(counted)
                                            tot_sys += Decimal(str(a_q))
                                            tot_qdif += Decimal(diff_qty)
                                            tot_vdif += Decimal(diff_qty) * Decimal(sell_price)

                                if doc == 'preview':
                                    header['entries'] = entries
                                    header['values'] = values
                                    response['message'] = {
                                        'header': header, 'trans': {'counted': arr, 'not_counted': not_arr}
                                    }
                                elif doc == 'excel':
                                    sheet[f'A2'] = "SUMMARY"
                                    sheet['D2'] = tot_phy
                                    sheet['E2'] = tot_sys
                                    sheet['F2'] = tot_qdif
                                    sheet['G2'] = "-"
                                    sheet['H2'] = tot_vdif
                                    from datetime import datetime
                                    current_datetime = datetime.now()
                                    formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
                                    file = f"static/general/tmp/{stock_hd.loc}_{g_name.strip().replace(' ', '_')}_AS_OF_{as_of}_{formatted_datetime}.xlsx"
                                    workbook.save(file)
                                    response['message'] = file

                                response['status_code'] = 200
                                response['status'] = 'success'
                            else:
                                response['message'] = "NO OPEN STOCK"
                                response['status_code'] = 404
                                response['status'] = 'limit'

                    elif stage == 'frozen':
                        pk = data.get('pk')

                        # check if hd exist
                        hd_x = StockFreezeHd.objects.filter(pk=pk)

                        if hd_x.count() == 1:
                            response['status_code'] = 200

                            hd = StockFreezeHd.objects.get(pk=pk)
                            trans = hd.trans()

                            header = {
                                'pk':hd.pk,
                                'loc':hd.loc_id,
                                'remarks':hd.remarks,
                                'ref':hd.ref,
                                'time':f"{hd.created_date} {hd.created_time}",
                                'status':hd.status,
                                'owner':hd.owner.username,
                                'next':hd.next(),
                                'prev':hd.prev()
                            }

                            tr = []

                            for t in trans['trans']:
                                print(t)
                                ref = t.item_ref
                                barcode = t.barcode
                                name = t.name
                                qty = t.qty

                                tr.append({
                                    'item_ref': ref,
                                    'barcode': barcode,
                                    'name': name,
                                    'qty': qty
                                })

                            response['message'] = {
                                    'header':header,
                                    'count': trans['count'],
                                    'trans': tr
                                }

                        else:
                            response['status_code'] = 404
                            response['message'] = f"Expected 1 but got {hd_x.count()} counts"


            except Exception as e:
                response['status'] = 'error'
                response['status_code'] = 505
                # Get the line number where the exception occurred
                line_number = traceback.extract_tb(e.__traceback__)[-1].lineno

                # Set the message with the line number
                response['message'] = f"Error occurred at line {line_number}: {str(e)}"

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
                elif stage == 'comment':
                    comment_pk = data.get('comment_pk')
                    comment = data.get('comment')
                    issue = data.get('issue')

                    if StockCountTrans.objects.filter(pk=comment_pk).count() == 1:
                        # update
                        coun = StockCountTrans.objects.get(pk=comment_pk)
                        coun.comment = comment
                        coun.issue = issue
                        coun.save()
                        response['message'] = "Comment Updated"
                    else:
                        response['message'] = f"No count with pk as {comment_pk}"
                elif stage == 'save_frozen':

                    header = data.get('header')
                    trans = data.get('trans')

                    if len(trans) > 0:

                        try:
                            loc_id = header.get('loc')
                            frozen_ref = header.get('frozen_ref')
                            remarks = header.get('remarks')
                            us_pk = header.get('owner')

                            owner = get_object_or_404(User, pk=us_pk)
                            stock_freeze_hd = StockFreezeHd.objects.create(loc_id=loc_id, ref=frozen_ref,
                                                                           remarks=remarks, owner=owner)

                            try:
                                for tran in trans:
                                    ref = tran['ref']
                                    barcode = tran['barcode']
                                    qty = tran['qty']
                                    name = tran['name']

                                    StockFreezeTrans.objects.create(entry_id=stock_freeze_hd.pk, item_ref=ref,
                                                                    barcode=barcode, qty=qty, name=name)

                                response['message'] = "SAVED"
                                response['status_code'] = 200
                            except Exception as e:
                                stock_freeze_hd.delete()
                                response['message'] = str(e)

                        except Exception as e:
                            response['message'] = str(e)


                    else:

                        response['message'] = f" {len(trans)} Transactions cannot be empty"
                        response['status'] = "EMPTY"
                        response['status_code'] = 100

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
        response["message"] = f"Error decoding JSON: {str(e)}"

    return JsonResponse(response)
