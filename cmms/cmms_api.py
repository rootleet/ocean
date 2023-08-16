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

from cmms.extra import db

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

                    elif stage == 'preview':
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
                                trans = StockCountTrans.objects.filter(stock_count_hd=stock_hd)
                                frozen = stock_hd.frozen
                                header = {
                                    'frozen': {
                                        'pk': frozen.pk,
                                        'loc': frozen.loc_id,
                                        'remarks': frozen.remarks,
                                        'status': frozen.status,
                                        'owner': frozen.owner.username,
                                        'created': f"{frozen.created_date} {frozen.created_time}",
                                        'entry': frozen.ent(),
                                        'posted': frozen.posted()

                                    },
                                    'count': {
                                        'pk': stock_hd.pk,
                                        'entry': stock_hd.entry_no(),
                                        'created': stock_hd.created_at,
                                        'comment': stock_hd.comment,
                                        'status': stock_hd.status,
                                        'owner': stock_hd.owner.username,
                                        'next': stock_hd.next(),
                                        'prev': stock_hd.prev(),
                                        'approved': stock_hd.approve
                                    }
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
                                for tran in trans:
                                    comment = "NO COMMENT"
                                    if len(tran.comment) > 0:
                                        comment = tran.comment
                                    arr.append({
                                        'item_ref': tran.item_ref,
                                        'barcode': tran.barcode,
                                        'name': tran.name,
                                        'froze_qty': tran.froze_qty,
                                        'counted_qty': tran.counted_qty,
                                        'diff_qty': tran.diff_qty,
                                        'comment': comment,
                                        'issue': tran.issue
                                    })

                                if doc == 'preview':
                                    header['entries'] = entries
                                    header['values'] = values
                                    response['message'] = {
                                        'header': header, 'trans': arr
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

                        elif style == 'count_sheet':
                            print(data)
                            doc = data.get('doc')
                            key = data.get('key')
                            print(doc)

                            if doc == 'fr':
                                # frozen
                                if StockFreezeHd.objects.filter(pk=key).count() == 1:

                                    f_hd = StockFreezeHd.objects.get(pk=key)
                                    trans = f_hd.trans_only()

                                    pdf = FPDF('P', 'mm', 'A4')
                                    pdf.add_page()
                                    pdf.set_font('Arial', 'BU', 10)
                                    pdf.cell(180, 5, "STOCK COUNT SHEET", 0, 1, 'C')
                                    pdf.ln(10)

                                    pdf.set_font('Arial', 'B', 10)
                                    pdf.cell(25, 5, "LOCATION : ", 0, 0, 'L')
                                    pdf.set_font('Arial', '', 7)
                                    pdf.cell(80, 5, f" {f_hd.loc_id}", 0, 1, 'L')

                                    pdf.set_font('Arial', 'B', 10)
                                    pdf.cell(25, 5, "REMARKS : ", 0, 0, 'L')
                                    pdf.set_font('Arial', '', 7)
                                    pdf.cell(80, 5, f" {f_hd.remarks}", 0, 1, 'L')
                                    pdf.ln(10)
                                    # header
                                    pdf.set_font('Arial', 'B', 10)
                                    pdf.cell(10, 5, f"LN", 1, 0, 'L')
                                    pdf.cell(10, 5, f"LN", 1, 0, 'L')
                                    pdf.cell(25, 5, f"ITEM REF", 1, 0, 'L')
                                    pdf.cell(30, 5, f"BARCODE", 1, 0, 'L')
                                    pdf.cell(100, 5, f"NAME", 1, 0, 'L')
                                    # pdf.cell(20, 5, f"FROZEN", 1, 0, 'L')
                                    pdf.cell(20, 5, f"COUNTED", 1, 1, 'L')

                                    pdf.set_font('Arial', '', 7)

                                    line = 0

                                    for tran in trans:
                                        line += 1
                                        pdf.cell(10, 5, f"{line}", 1, 0, 'L')
                                        pdf.cell(25, 5, f"{tran.item_ref}", 1, 0, 'L')
                                        pdf.cell(30, 5, f"{tran.barcode}", 1, 0, 'L')
                                        pdf.cell(100, 5, f"{tran.name}", 1, 0, 'L')
                                        # pdf.cell(20, 5, f"{tran.qty}", 1, 0, 'L')
                                        pdf.cell(20, 5, f"", 1, 1, 'L')

                                    file = f'static/general/tmp/{f_hd.loc_id}.pdf'
                                    pdf.output(file, 'F')

                                    response = {
                                        'status_code': 200, 'message': file, 'status': 'success'
                                    }
                                else:
                                    response = {
                                        'status_code': 404, 'message': "ENTRY NOT FOUND", 'status': 'not_found'
                                    }
                            elif doc == 'stc':
                                if StockCountHD.objects.filter(pk=key).count() == 1:
                                    hd = StockCountHD.objects.get(pk=key)
                                    f_hd = hd.frozen
                                    trans = hd.trans()
                                    trans_only = trans['trans']

                                    pdf = FPDF('P', 'mm', 'A4')
                                    pdf.add_page()
                                    pdf.set_font('Arial', 'BU', 10)
                                    pdf.cell(180, 5, "COUNT REPORT", 0, 1, 'C')
                                    pdf.ln(10)

                                    pdf.set_font('Arial', 'B', 10)
                                    pdf.cell(25, 5, "LOCATION : ", 0, 0, 'L')
                                    pdf.set_font('Arial', '', 7)
                                    pdf.cell(80, 5, f" {f_hd.loc_id}", 0, 1, 'L')

                                    pdf.set_font('Arial', 'B', 10)
                                    pdf.cell(25, 5, "REMARKS : ", 0, 0, 'L')
                                    pdf.set_font('Arial', '', 7)
                                    pdf.cell(80, 5, f" {f_hd.remarks}", 0, 1, 'L')
                                    pdf.ln(10)
                                    # header
                                    pdf.set_font('Arial', 'B', 8)
                                    pdf.cell(10, 5, f"LN", 1, 0, 'L')
                                    pdf.cell(20, 5, f"BARCODE", 1, 0, 'L')
                                    pdf.cell(55, 5, f"NAME", 1, 0, 'L')
                                    pdf.cell(15, 5, f"SELL", 1, 0, 'L')
                                    pdf.cell(15, 5, f"FRZN", 1, 0, 'L')
                                    pdf.cell(15, 5, f"FR VL", 1, 0, 'L')
                                    pdf.cell(15, 5, f"CT", 1, 0, 'L')
                                    pdf.cell(15, 5, f"CT VL", 1, 0, 'L')
                                    pdf.cell(15, 5, f"DIFF", 1, 0, 'L')
                                    pdf.cell(15, 5, f"DF VL", 1, 1, 'L')
                                    pdf.set_font('Arial', '', 5)
                                    line = 0
                                    summary = trans['summary']
                                    pdf.cell(100, 5, f"SUMMARY", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['total_frozen']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['value_frozen']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['total_counted']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['value_counted']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['qty_difference']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['value_difference']}", 1, 1, 'L')

                                    pdf.set_font('Arial', '', 5)
                                    for tran in trans_only:
                                        line += 1
                                        pdf.cell(10, 5, f"{line}", 1, 0, 'L')
                                        pdf.cell(20, 5, f"{tran.barcode}", 1, 0, 'L')
                                        pdf.cell(55, 5, f"{tran.name}", 1, 0, 'L')
                                        pdf.cell(15, 5, f"{tran.sell_price}", 1, 0, 'L')
                                        pdf.cell(15, 5, f"{tran.froze_qty}", 1, 0, 'L')
                                        pdf.cell(15, 5, f"{tran.froze_qty * tran.sell_price}", 1, 0, 'L')
                                        pdf.cell(15, 5, f"{tran.counted_qty}", 1, 0, 'L')
                                        pdf.cell(15, 5, f"{tran.counted_qty * tran.sell_price}", 1, 0, 'L')
                                        pdf.cell(15, 5, f"{tran.diff_qty}", 1, 0, 'L')
                                        pdf.cell(15, 5, f"{tran.diff_qty * tran.sell_price}", 1, 1, 'L')

                                        # summary

                                    pdf.set_font('Arial', 'B', 8)
                                    pdf.cell(100, 5, f"SUMMARY", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['total_frozen']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['value_frozen']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['total_counted']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['value_counted']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['qty_difference']}", 1, 0, 'L')
                                    pdf.cell(15, 5, f"{summary['value_difference']}", 1, 1, 'L')

                                    file = f'static/general/tmp/{hd.entry_no()}.pdf'
                                    pdf.output(file, 'F')

                                    response = {
                                        'status_code': 200, 'message': file, 'status': 'success'
                                    }


                                else:
                                    response = {
                                        'status_code': 404, 'message': "ENTRY NOT FOUND", 'status': 'not_found'
                                    }
                            else:
                                response['message'] = f"UNKNOWN DOCUMENT {doc}"

                    elif stage == 'frozen':
                        pk = data.get('pk')

                        # check if hd exist
                        hd_x = StockFreezeHd.objects.filter(pk=pk)

                        if hd_x.count() == 1:
                            response['status_code'] = 200

                            hd = StockFreezeHd.objects.get(pk=pk)
                            trans = hd.trans()

                            header = {
                                'pk': hd.pk,
                                'loc': hd.loc_id,
                                'remarks': hd.remarks,
                                'ref': hd.ref,
                                'time': f"{hd.created_date} {hd.created_time}",
                                'status': hd.status,
                                'owner': hd.owner.username,
                                'next': hd.next(),
                                'prev': hd.prev(),
                                'approve': hd.approve
                            }

                            tr = []

                            for t in trans['trans']:
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
                                'header': header,
                                'count': trans['count'],
                                'trans': tr
                            }

                        else:
                            response['status_code'] = 404
                            response['message'] = f"Expected 1 but got {hd_x.count()} counts"

                    elif stage == 'frozen_hd':

                        frozn = StockFreezeHd.objects.filter(status=1).order_by('-pk')
                        counts = frozn.count()
                        arr = []
                        for fr in frozn:
                            arr.append({
                                'pk': fr.pk,
                                'entry': f"FR{fr.loc_id}{fr.pk}",
                                'remarks': fr.remarks,
                                'location': fr.loc_id,
                                'approve': fr.approve,
                                'posted': fr.posted()
                            })

                        response['message'] = arr
                        response['status_code'] = 200

                    elif stage == 'ref_frozen':
                        try:
                            server = f"{DB_SERVER},{DB_PORT}"
                            database = DB_NAME
                            username = DB_USER
                            password = DB_PASSWORD
                            driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
                            connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
                            connection = pyodbc.connect(connection_string)
                            cursor = connection.cursor()

                            ref = data.get('ref')
                            query = f"SELECT item_ref,qty_avail,unit_price,(SELECT barcode from product_master where item_ref = stock_freeze_tran.item_ref ) as 'barcode',(SELECT item_des1 from product_master where item_ref = stock_freeze_tran.item_ref ) as 'name' from stock_freeze_tran where entry_no = '{ref}'"
                            trans = []
                            cursor.execute(query)
                            count = 0
                            for tran in cursor.fetchall():
                                count += 1
                                trans.append({
                                    'item_ref': str(tran[0].strip()),
                                    'qty': tran[1],
                                    'unit_price': tran[2],
                                    'barcode': str(tran[3]).strip(),
                                    'name': str(tran[4]).strip()
                                })

                            # get header
                            h_q = f"SELECT loc_id,remarks from stock_freeze_hd where entry_no = '{ref}'"
                            h_row = cursor.execute(h_q).fetchone()

                            if h_row is None:
                                loc = 'none',
                                rem = 'none'
                            else:
                                loc = str(h_row[0]).strip()
                                rem = str(h_row[1]).strip()

                            header = {
                                'loc': loc, 'remarks': rem
                            }

                            response['message'] = {
                                'header': header,
                                'count': count,
                                'trans': trans
                            }

                            response['status_code'] = 200
                        except Exception as e:
                            response['status_code'] = 500
                            response['message'] = str(e)

                    elif stage == 'export':
                        doc = data.get('doc')
                        key = data.get('key')
                        document = data.get('document')

                        if doc == 'STC':
                            # count
                            hd = StockCountHD.objects.filter(pk=key)
                        elif doc == 'STR':
                            # sales transactions
                            hd = SalesCustomers.objects.filter(pk=key)
                        count = hd.count()
                        if count == 1:
                            response['status_code'] = 200
                            header = hd.last()
                            trans = header.trans()

                            if document == 'csv' and doc == 'STC':
                                file_name = f"static/general/tmp/{header.frozen.loc_id} - {header.frozen.remarks}.csv"
                                # Header
                                header = ["ITEM_REF",  "COUNTED"]

                                with open(file_name, mode="w", newline='') as file:
                                    writer = csv.writer(file)

                                    # Writing the header
                                    writer.writerow(header)

                                    for tran in trans['trans']:
                                        if tran.counted_qty > 0:
                                            counted_qty = tran.counted_qty
                                        else:
                                            counted_qty = tran.counted_qty

                                        writer.writerow(
                                            [tran.item_ref, counted_qty])

                                response['message'] = file_name

                            elif document == 'excel' and doc == 'STC':
                                import openpyxl
                                workbook = openpyxl.Workbook()
                                sheet = workbook.active
                                # make sheet head
                                sheet['A1'] = f"LOCATION : {header.frozen.loc_id}"
                                sheet['A2'] = f"REFERENCE : {header.frozen.ref}"
                                sheet['A3'] = f"REMARK : {header.frozen.remarks}"

                                sheet[f'A5'] = "ITEM REFERENCE"
                                sheet[f'B5'] = "BARCODED"
                                sheet[f'C5'] = "DESCRIPTION"
                                sheet[f'D5'] = "FROZEN QTY"
                                sheet[f'E5'] = "COUNTED QTY"
                                sheet[f'F5'] = "DIFFERENCE"

                                sheet['A6'] = "SUMMARY"
                                sheet['D6'] = trans['summary']['total_frozen']
                                sheet['E6'] = trans['summary']['total_counted']
                                sheet['F6'] = trans['summary']['qty_difference']

                                row = 7
                                for tran in trans['trans']:
                                    row += 1
                                    sheet[f"A{row}"] = tran.item_ref
                                    sheet[f"B{row}"] = tran.barcode
                                    sheet[f"C{row}"] = tran.name
                                    sheet[f"D{row}"] = tran.froze_qty
                                    sheet[f"E{row}"] = tran.counted_qty
                                    sheet[f"F{row}"] = tran.diff_qty

                                from datetime import datetime
                                current_datetime = datetime.now()
                                formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
                                file = f"static/general/tmp/{doc}_{header.frozen.ref}.xlsx"
                                workbook.save(file)
                                response['message'] = file

                            elif document == 'excel' and doc == "STR":
                                import openpyxl
                                workbook = openpyxl.Workbook()
                                sheet = workbook.active
                                # make sheet head
                                sheet['A1'] = f"DATE"
                                sheet['B1'] = f"BY"
                                sheet['C1'] = f"TITLE"
                                sheet['D1'] = "Description"

                                # loop through transactins
                                count = 1
                                for tran in header.trans():
                                    count += 1
                                    sheet[f'A{count}'] = f"{tran.created_date} {tran.created_time}"
                                    sheet[f'B{count}'] = f"{tran.owner.username}"
                                    sheet[f'C{count}'] = f"{tran.title}"
                                    sheet[f'D{count}'] = f"{tran.details}"

                                from datetime import datetime
                                current_datetime = datetime.now()
                                formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
                                file = f"static/general/tmp/{doc}_{header.name}.xlsx"
                                workbook.save(file)
                                response['message'] = file

                        else:
                            response['status_code'] = 404
                            response['message'] = f"ENTRY NOT FOUNC ( {doc} - {key} )"

                elif module == 'customer':
                    cust_type = data.get('cust_type')
                    if cust_type == 'cmms_service':
                        cursor = db()
                        cust_code = data.get('cust_code') or 'all'
                        if cust_code == 'all':
                            cursor.execute("select cust_code,cust_name,cust_contact,email1 from customer_master")
                        else:
                            cursor.execute(f"select cust_code,cust_name,cust_contact,email1 from customer_master  where cust_code = '{cust_code}'")
                        cust_arr = []
                        for customer in cursor.fetchall():
                            cust_arr.append({
                                'code': str(customer[0]).strip(),
                                'name': str(customer[1]).strip(),
                                'phone': str(customer[2]).strip(),
                                'email': str(customer[3]).strip()
                            })
                        response['message'] = cust_arr
                        response['status_code'] = 200

                elif module == 'cust_asset':
                    customer = data.get('customer')

                    # check if customer exist
                    cust_count = db().execute(
                        f"SELECT COUNT(*) FROM customer_master where cust_code = '{customer}'").fetchone()[0]
                    if cust_count == 1:
                        # customer details
                        customer_details = db().execute(
                            f"select cust_code,cust_name,cust_contact,email1 from customer_master "
                            f"where cust_code = '{customer}'").fetchone()
                        header = {
                            'code': customer,
                            'name': str(customer_details[1]).strip(),
                            'phone': str(customer_details[2]).strip()
                        }
                        assets_q = f"select ASSET_CODE,asset_desc,asset_no,asset_ref_no,model_no from asset_mast where cust_code = '{customer}'"
                        asset_arr = []
                        asset_cursor = db()
                        asset_cursor.execute(assets_q)
                        # db().execute(assets_q)

                        for asset in asset_cursor.fetchall():
                            obj = {
                                'code': str(asset[0]).strip(),
                                'name': str(asset[1]).strip(),
                                'number': str(asset[2]).strip(),
                                'chassis': str(asset[3]).strip(),
                                'model': str(asset[4]).strip(),
                            }
                            asset_arr.append(obj)

                        response['status_code'] = 200
                        response['message'] = {
                            'customer': header, 'assets': asset_arr
                        }
                    else:
                        response['status_code'] = 404
                        response['message'] = f"NO CUSTOMER WITH CODE {customer}"

                elif module == 'service_history':
                    asset = data.get('asset')
                    db().execute(
                        f"select Entry_no,Invoice_date,wo_date,tot_amt,tax_amt,net_amt,labor_amount,material_amount from invoice_hd where asset_code = '{asset}' order by Invoice_date desc")
                    serv_arr = []
                    for service in db().fetchall():

                        # get materials
                        db().execute(
                            f"select invoice_type,descr,uom,unit_qty,unit_price,tot_amt,tax_amt,net_amt from invoice_tran where Entry_no = '{service[0]}'")
                        tran_arr = []
                        for tran in db().fetchall():
                            tobj = {
                                'type': str(tran[0]).strip(),
                                'name': str(tran[1]).strip(),
                                'packing': str(tran[2]).strip(),
                                'unit_qty': str(tran[3]).strip(),
                                'unit_price': str(tran[4]).strip(),
                                'net': str(tran[5]).strip(),
                                'tax': str(tran[6]).strip(),
                                'gross': str(tran[7]).strip()
                            }
                            tran_arr.append(tobj)

                        obj = {
                            'invoice': str(service[0]).strip(),
                            'date': str(service[1]).strip(),
                            'tot_amt': str(service[3]).strip(),
                            'tax_amt': str(service[4]).strip(),
                            'net_amt': str(service[5]).strip(),
                            'lab_amt': str(service[6]).strip(),
                            'mat_amt': str(service[7]).strip(),
                            'trans': tran_arr
                        }
                        serv_arr.append(obj)

                    # db().close()
                    response['status_code'] = 200
                    response['message'] = serv_arr

                elif module == 'invoice_detail':
                    invoice = data.get('invoice')
                    header = {}
                    assets = {}
                    trans = []

                    inv_hd = db().execute(f"select Entry_no,Invoice_date,tot_amt,tax_amt,net_amt,labor_amount,material_amount,asset_code from invoice_hd where Entry_no= '{invoice}'").fetchone()
                    header['invoice_no'] = str(inv_hd[0]).strip()
                    header['date'] = str(inv_hd[1]).strip()
                    header['net'] = str(inv_hd[2]).strip()
                    header['tax'] = str(inv_hd[3]).strip()
                    header['gross'] = str(inv_hd[4]).strip()
                    header['lab'] = str(inv_hd[5]).strip()
                    header['mat'] = str(inv_hd[6]).strip()

                    # asset details
                    asset_code = inv_hd[7]
                    asset = db().execute(f"select ASSET_CODE,asset_desc,asset_no,asset_ref_no,model_no,cust_code from asset_mast where ASSET_CODE = '{asset_code}'").fetchone()
                    assets['code'] = str(asset[0]).strip()
                    assets['name'] = str(asset[1]).strip()
                    assets['number'] = str(asset[2]).strip()
                    assets['chassis'] = str(asset[3]).strip()
                    assets['model'] = str(asset[4]).strip()
                    assets['owner'] = str(asset[5]).strip()


                    db().execute(f"select invoice_type,descr,uom,unit_qty,unit_price,tot_amt,tax_amt,net_amt from invoice_tran where Entry_no = '{invoice}'")
                    for tran in db().fetchall():
                        tobj = {
                            'type': str(tran[0]).strip(),
                            'name': str(tran[1]).strip(),
                            'packing': str(tran[2]).strip(),
                            'unit_qty': str(tran[3]).strip(),
                            'unit_price': str(tran[4]).strip(),
                            'net': str(tran[5]).strip(),
                            'tax': str(tran[6]).strip(),
                            'gross': str(tran[7]).strip()
                        }
                        trans.append(tobj)

                    response['message'] = {
                        'header':header,'asset':assets,'trans':trans
                    }
                    response['status_code'] = 200

                elif module == 'just_costomer':
                    cust_code = data.get('code')
                    db().execute(
                        f"SELECT cust_name, cust_contact, email1, email2 FROM customer_master WHERE cust_code = '{cust_code}'"
                    )

                    row = db().fetchone()
                    if row:
                        response = {
                            'status_code': 200,
                            'message': {
                                'name': str(row[0]).strip(),
                                'phone': str(row[1]).strip(),
                                'email': str(row[2]).strip()
                            }
                        }
                    else:
                        response = {
                            'status_code': 404,
                            'message': 'Customer not found'
                        }

                elif module == 'cmms_sales_customer':
                    key = data.get('key')
                    arr = []

                    if key == 'all':
                        customers = SalesCustomers.objects.all()
                    else:
                        customers = SalesCustomers.objects.filter(pk=key)

                    if customers.count() > 0:
                        for customer in customers:
                            x_region = getattr(customer.region, 'name', 'UNKNOWN') if customer and hasattr(customer, 'region') else 'unknown'
                            suburb = getattr(customer.suburb, 'name', 'UNKNOWN') if customer and hasattr(customer, 'suburb') else 'unknown'

                            obj = {
                                'pk':customer.pk,
                                'url':customer.url,
                                'company':customer.company,
                                'name':customer.name,
                                'mobile':customer.mobile,
                                'email':customer.email,
                                'address':customer.address,
                                'type_of_client':customer.type_of_client,
                                'timestamp':{
                                    'created_date':customer.created_date,
                                    'created_time':customer.created_time,
                                    'updated_date':customer.updated_date,
                                    'updated_time':customer.updated_time
                                },
                                'status':customer.status,
                                'owner':{
                                    'pk':customer.owner.pk,
                                    'username':customer.owner.username
                                },
                                'geography':{
                                    'region':x_region,
                                    'suburb':suburb
                                }

                            }
                            arr.append(obj)

                        response['status_code'] = 200
                        response['message'] = arr
                    else:
                        response['status_code'] = 404
                        response['message'] = f"NO CUSTOMER FOUND WITH KEY {key}"

                elif module == 'cmms_sales_deals':
                    cust = data.get('sales_customer')
                    if SalesCustomers.objects.filter(pk=cust).count() == 1:
                        customer = SalesCustomers.objects.get(pk=cust)
                        deals = customer.deals()
                        deal_arr = []
                        for deal in deals:
                            obj = {
                                'sales_rep':{
                                    'pk':deal.owner.pk,
                                    'username':deal.owner.username
                                },
                                'purch_rep':{
                                    'name':deal.pur_rep_name,
                                    'email':deal.pur_rep_email,
                                    'phone':deal.pur_rep_phone,
                                    'company':deal.customer.company
                                },
                                'asset':{
                                    'name':deal.asset,
                                    'model':deal.model,
                                    'stock_type':deal.stock_type,
                                    'requirement':deal.requirement
                                },
                                'status':deal.status,
                                'date': deal.created_date,
                                'time': deal.created_time,
                                'pk':deal.pk

                            }
                            deal_arr.append(obj)
                        response['status_code'] = 200
                        response['message'] = deal_arr

                    else:
                        response['status_code'] = 404
                        response['message'] = f"CUSTOMER DOES NOT EXIST"

                elif module == 'cmms_sales_deal':
                    dealkey = data.get('deal')

                    try:
                        deal = SalesDeals.objects.get(pk=dealkey)
                        trans = deal.transactions()
                        transactions = []
                        for tran in trans:
                            obj = {
                                'title':tran.title,
                                'details':tran.details,
                                'owner':{
                                    'pk':tran.owner.pk,
                                    'username':tran.owner.username
                                },
                                'timestamp':{
                                    'd_created':tran.created_date,
                                    't_created':tran.created_time
                                }
                            }
                            transactions.append(obj)

                        header = {
                            'sales_rep':{
                                    'pk':deal.owner.pk,
                                    'username':deal.owner.username
                            },
                            'purch_rep':{
                                    'name':deal.pur_rep_name,
                                    'email':deal.pur_rep_email,
                                    'phone':deal.pur_rep_phone,
                                    'company':deal.customer.company
                            },
                            'asset':{
                                    'name':deal.asset,
                                    'model':deal.model,
                                    'stock_type':deal.stock_type,
                                    'requirement':deal.requirement
                            },
                            'status':deal.status,
                            'date': deal.created_date,
                            'time': deal.created_time
                        }

                        response['status_code'] = 200
                        response['message'] = {
                            'deal':header,'trans':transactions
                        }

                    except Exception as e:
                        response['status_code'] = 505
                        response['message'] = str(e)

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
                                line_number = traceback.extract_tb(e.__traceback__)[-1].lineno
                                response['message'] = f"Error occurred at line {line_number}: {str(e)}"

                        except Exception as e:
                            line_number = traceback.extract_tb(e.__traceback__)[-1].lineno
                            response['message'] = f"Error occurred at line {line_number}: {str(e)}"


                    else:

                        response['message'] = f" {len(trans)} Transactions cannot be empty"
                        response['status'] = "EMPTY"
                        response['status_code'] = 100
                elif stage == 'save_cont':
                    header = data.get('header')
                    trans = data.get('trans')
                    count_pk = header.get('count_pk')
                    task = header.get('task')

                    frozen_ref = header.get('ref')
                    comment = header.get('comment')
                    owner_pk = header.get('owner_pk')
                    owner = User.objects.get(pk=owner_pk)

                    if StockFreezeHd.objects.filter(pk=frozen_ref).count() == 1:
                        try:

                            frozen = StockFreezeHd.objects.get(pk=frozen_ref)
                            frozen.status = 2

                            if StockCountHD.objects.filter(frozen=frozen, comment=comment, owner=owner).exists():
                                # delete
                                StockCountHD.objects.get(frozen=frozen, comment=comment, owner=owner).delete()
                            StockCountHD(frozen=frozen, comment=comment, owner=owner).save()
                            count_hd = StockCountHD.objects.get(frozen=frozen, comment=comment, owner=owner)

                            # save trans
                            for tran in trans:
                                print(tran)
                                ref = tran.get('ref')
                                barcode = tran.get('barcode')
                                name = tran.get('name')
                                frozen = tran.get('frozen')
                                counted = tran.get('counted')
                                diff = tran.get('diff')
                                row_comment = tran.get('row_comment')
                                row_iss = tran.get('row_iss')

                                # get this item value
                                cursor = db()

                                q = f"SELECT sell_price FROM product_master where barcode = '{barcode}'"
                                value = cursor.execute(q).fetchone()[0]
                                if value is None:
                                    value = 0.00

                                print({'VAL': value, 'diff': Decimal(str(diff)), 'frozen': Decimal(str(frozen)),
                                       'counted': Decimal(counted)})

                                diff_val = Decimal(value) * Decimal(diff)
                                froze_val = Decimal(value) * Decimal(frozen)
                                counted_val = Decimal(value) * Decimal(counted)

                                cursor.close()

                                # save tran
                                StockCountTrans.objects.create(stock_count_hd=count_hd, item_ref=ref, barcode=barcode,
                                                               name=name, froze_qty=frozen, counted_qty=counted,
                                                               diff_qty=diff, comment=row_comment, issue=row_iss,
                                                               froze_val=froze_val, diff_val=diff_val,
                                                               counted_val=counted_val)

                            frozen.save()
                            response['status_code'] = 200
                            response['status'] = 'success'
                            response['message'] = "Stock Count Saved"



                        except Exception as e:
                            response['status_code'] = 500
                            response['status'] = 'error'
                            line_number = traceback.extract_tb(e.__traceback__)[-1].lineno
                            response['message'] = f"Error occurred at line {line_number}: {str(e)}"



                    else:
                        response['statys_code'] = 404
                        response['message'] = f"CANNOT FIND FROZEN with entry {frozen_ref}"

            elif module == 'sales_deal':
                sales_rep = data.get('sales_rep')
                sales_cust = data.get('sales_customer')

                pur_rep_name = data.get('pur_rep_name')
                pur_rep_email = data.get('pur_rep_email')
                pur_rep_phone = data.get('pur_rep_phone')

                asset = data.get('asset')
                model = data.get('model')

                stock_type = data.get('stock_type')
                requirement = data.get('requirement')

                # validate
                try:
                    customer = SalesCustomers.objects.get(pk=sales_cust)
                    owner = User.objects.get(pk=sales_rep)

                    SalesDeals(customer=customer,owner=owner,pur_rep_name=pur_rep_name,pur_rep_phone=pur_rep_phone,pur_rep_email=pur_rep_email,asset=asset,model=model,
                                      stock_type=stock_type,requirement=requirement).save()
                    response['status_code'] = 200
                    response['message'] = "DEAL CREATED"
                except Exception as e:
                    response['status_code'] = 505
                    response['message']  = str(e)

            elif module == 'deal_transaction':
                dealkey = data.get('deal')
                title = data.get('title')
                detail = data.get('detail')
                ownerkey = data.get('owner')



                try:
                    deal = SalesDeals.objects.get(pk=dealkey)
                    owner = User.objects.get(pk=ownerkey)
                    DealTransactions(deal=deal,title=title,details=detail,owner=owner).save()

                    response['status_code'] = 200
                    response['message'] = "TRANSACTION ADDED"
                except Exception as e:
                    response['status_code'] = 500
                    response['message'] = str(e)



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

                if stage == 'save_cont':
                    header = data.get('header')
                    count_pk = header.get('count_pk')

                    print(data)

                    # print(data)
                    if StockCountHD.objects.filter(pk=count_pk).count() == 1:
                        c_hd = StockCountHD.objects.get(pk=count_pk)
                        c_hd.comment = header.get('comment')

                        trans = data.get('trans')

                        # delete all trans
                        # delete this tran and add again

                        for tran in trans:

                            print(tran)
                            ref = tran.get('ref')
                            barcode = tran.get('barcode').strip()
                            name = tran.get('name')
                            frozen = tran.get('frozen')
                            counted = str(tran.get('counted'))
                            diff = tran.get('diff')
                            row_comment = tran.get('row_comment')
                            row_iss = tran.get('row_iss')
                            StockCountTrans.objects.filter(stock_count_hd=c_hd, item_ref=ref).delete()
                            cursor = db()
                            q = f"SELECT sell_price FROM product_master where barcode = '{barcode}'"

                            if cursor.execute(q).fetchone() is None:
                                value = 0.00
                            else:
                                value = cursor.execute(q).fetchone()[0]

                            diff_val = Decimal(value) * Decimal(diff)
                            froze_val = Decimal(value) * Decimal(frozen)
                            counted_val = Decimal(value) * Decimal(counted)

                            cursor.close()

                            # save tran
                            StockCountTrans.objects.create(stock_count_hd=c_hd, item_ref=ref, barcode=barcode,
                                                           name=name, froze_qty=frozen, counted_qty=counted,
                                                           diff_qty=diff, comment=row_comment, issue=row_iss,
                                                           diff_val=diff_val, froze_val=froze_val,
                                                           counted_val=counted_val, sell_price=value)
                        c_hd.save()
                        response['message'] = "UPDATE SUCCESSFUL"
                    else:
                        var = response['status_code'] = 404
                        response['message'] = f"CANNOT FIND DOCUMENT with key {count_pk}"

            elif module == 'approve':
                doc = data.get('doc')
                key = data.get('key')

                if doc == 'FR':
                    hd = StockFreezeHd.objects.filter(pk=key)
                    count = hd.count()
                elif doc == 'STK':
                    # approved counted stock
                    hd = StockCountHD.objects.filter(pk=key)
                    count = hd.count()
                else:
                    count = 0

                if count == 1:
                    try:
                        head = hd.last()
                        head.approve = 1
                        head.save()

                        response['status_code'] = 200
                        response['status'] = 'success'
                        response['message'] = f"APPROVED {doc} = {key}"
                    except Exception as e:
                        response['status_code'] = 505
                        response['status'] = 'error'
                        response['message'] = str(e)

                else:
                    response['status_code'] = 404
                    response['status'] = 'error'
                    response['message'] = f"Count not find matching document ({doc} - {key})"


        elif method == 'DELETE':
            module = body.get('module') or 'before'
            doc = data.get('doc')
            key = data.get('key')
            if module == 'before':
                if doc == 'FR':
                    hd = StockFreezeHd.objects.filter(pk=key)
                    count = hd.count()
                elif doc == 'STK':
                    # approved counted stock
                    hd = StockCountHD.objects.filter(pk=key)
                    count = hd.count()
                else:
                    count = 0

                if count == 1:
                    try:
                        head = hd.last()
                        head.delete()

                        response['status_code'] = 200
                        response['status'] = 'success'
                        response['message'] = f"DELETED {doc} = {key}"
                    except Exception as e:
                        response['status_code'] = 505
                        response['status'] = 'error'
                        response['message'] = str(e)

                else:
                    response['status_code'] = 404
                    response['status'] = 'error'
                    response['message'] = f"Count not find matching document ({doc} - {key})"

            elif module == 'sales_customer':
                customer = SalesCustomers.objects.get(pk=data.get('key'))
                name = customer.name
                customer.delete()
                response['message'] = f"{name} deleted"

    except json.JSONDecodeError as e:
        response["status_code"] = 400
        response["status"] = "Bad Request"
        response["message"] = f"Error decoding JSON: {str(e)}"

    return JsonResponse(response)
