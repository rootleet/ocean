import json
import sys

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from admin_panel.models import Emails
from retail.db import ret_cursor, get_stock
from retail.models import BoltItems, BoltGroups


@csrf_exempt
def interface(request):
    response = {
        'status_code': 0,
        'message': ""
    }

    success_response = {
        'status_code': 200,
        'message': "Procedure Completed Successfully"
    }

    # get method
    method = request.method

    try:

        body = json.loads(request.body)
        module = body.get('module')
        data = body.get('data')

        if method == 'PUT':  # add bolt product
            if module == 'bolt_item':
                group = data.get('group')
                barcode = data.get('barcode')
                item_des = data.get('item_des')
                price = data.get('price')
                stock_nia = data.get('stock_nia')
                stock_spintex = data.get('stock_spintex')
                stock_osu = data.get('stock_osu')

                cursor = ret_cursor()
                qqq = f"SELECT retail1 from prod_mast where barcode = '{barcode}'"
                print(qqq)
                cursor.execute(qqq)
                prod = cursor.fetchone()

                if prod is None:
                    inv_price = 0.00
                else:
                    inv_price = prod[0]

                BoltItems(barcode=barcode, item_des=item_des, price=price, stock_osu=stock_osu,
                          stock_spintex=stock_spintex, stock_nia=stock_nia, group_id=group, inv_price=inv_price).save()
                success_response['message'] = "Product Added"

            elif module == 'bolt_group':  # add bolt group
                name = data.get('name')
                try:
                    BoltGroups(name=name).save()
                except Exception as e:
                    pass
                success_response['message'] = BoltGroups.objects.get(name=name).pk

        elif method == 'VIEW':
            if module == 'bolt_products':
                pk = data.get('key') or '*'

                if pk == '*':

                    items = BoltItems.objects.all()
                else:
                    items = BoltItems.objects.filter(Q(pk=pk) | Q(barcode=pk))

                item_list = []
                for item in items:
                    item_list.append({
                        'pk': item.pk,
                        'barcode': item.barcode,
                        'item_des': item.item_des,
                        'price': item.price,
                        'price_diff': item.price_diff,
                        'stock_nia': item.stock_nia,
                        'stock_spintex': item.stock_spintex,
                        'stock_osu': item.stock_osu,
                        'group': {
                            'pk': item.group.pk,
                            'name': item.group.name
                        }
                    })

                success_response['message'] = item_list

            elif module == 'bolt_group':
                pk = data.get('key') or '*'
                grps = []
                if pk == '*':
                    groups = BoltGroups.objects.all()
                else:
                    groups = BoltGroups.objects.filter(pk=pk)

                for group in groups:
                    grps.append({
                        'pk': group.pk,
                        'name': group.name
                    })

                success_response['message'] = grps

            elif module == 'price_change':
                send = data.get('send_mail') or 'no'
                cursor = ret_cursor()
                import openpyxl
                worksheet = openpyxl.Workbook()
                sheet = worksheet.active
                sheet['A1'] = "SKU"
                sheet['B1'] = "NAME"
                sheet['C1'] = "CURRENT PRICE"
                sheet['D1'] = "NEW PRICE"
                sheet_row = 2

                spintex_stock_book = openpyxl.Workbook()
                spintex_stock_sheet = spintex_stock_book.active

                spintex_stock_sheet['A1'] = "SKU"
                spintex_stock_sheet['B1'] = "NAME"
                spintex_stock_sheet['C1'] = "STOCK STATUS"
                spintex_stock_row = 2

                osu_stock_book = openpyxl.Workbook()
                osu_stock_sheet = osu_stock_book.active

                osu_stock_sheet['A1'] = "SKU"
                osu_stock_sheet['B1'] = "NAME"
                osu_stock_sheet['C1'] = "STOCK STATUS"
                osu_stock_row = 2

                nia_stock_book = openpyxl.Workbook()
                nia_stock_sheet = nia_stock_book.active
                nia_stock_sheet['A1'] = "SKU"
                nia_stock_sheet['B1'] = "NAME"
                nia_stock_sheet['C1'] = "STOCK STATUS"
                nia_stock_row = 2

                for item in BoltItems.objects.all():
                    barcode = item.barcode.replace('.0', '')

                    # get product detail

                    product = cursor.execute(
                        f"SELECT retail1,item_code,item_type from prod_mast where barcode = '{barcode}'").fetchone()
                    if product is not None:
                        price, item_code, item_type = product
                        if price != item.price:
                            # print("CHANGE")
                            sheet[f"A{sheet_row}"] = barcode
                            sheet[f"B{sheet_row}"] = item.item_des
                            sheet[f"C{sheet_row}"] = item.price
                            sheet[f"D{sheet_row}"] = product[0]
                            sheet_row += 1
                            item.price = price

                        # check stock and discontinues
                        stock = get_stock(item_code)
                        spintex = stock['spintex']
                        nia = stock['nia']
                        osu = stock['osu']

                        stock_spintex = 1 if spintex > 0 or item_type == '2' else 0
                        stock_osu = 1 if osu > 0 or item_type == '2' else 0
                        stock_nia = 1 if nia > 0 or item_type == '2' else 0

                        if stock_spintex != item.stock_spintex:
                            # change stock standing

                            spintex_stock_sheet[f"A{spintex_stock_row}"] = barcode
                            spintex_stock_sheet[f"B{spintex_stock_row}"] = item.item_des
                            spintex_stock_sheet[f"C{spintex_stock_row}"] = stock_spintex
                            item.stock_spintex = spintex

                            spintex_stock_row += 1

                        if stock_osu != item.stock_osu:
                            # change stock standing

                            osu_stock_sheet[f"A{osu_stock_row}"] = barcode
                            osu_stock_sheet[f"B{osu_stock_row}"] = item.item_des
                            osu_stock_sheet[f"C{osu_stock_row}"] = stock_osu
                            item.stock_osu = stock_osu

                            osu_stock_row += 1

                        if stock_nia != item.stock_nia:
                            # change stock standing

                            nia_stock_sheet[f"A{nia_stock_row}"] = barcode
                            nia_stock_sheet[f"B{nia_stock_row}"] = item.item_des
                            nia_stock_sheet[f"C{nia_stock_row}"] = stock_nia
                            item.stock_nia = stock_nia

                            nia_stock_row += 1

                price_count = sheet_row - 2
                nia_count = nia_stock_row - 2
                spintex_count = spintex_stock_row - 2
                osu_count = osu_stock_row - 2

                tr = ""
                if price_count > 0:
                    tr += f"<tr><td><strong>PRICE CHANGE</strong></td><td>{price_count}</td></tr>"
                if spintex_count > 0:
                    tr += f"<tr><td><strong>SPINTEX STOCK</strong></td><td>{spintex_count}</td></tr>"
                if nia_count > 0:
                    tr += f"<tr><td><strong>NIA</strong></td><td>{nia_count}</td></tr>"
                if osu_count > 0:
                    tr += f"<tr><td><strong>OSU STOCK</strong></td><td>{osu_count}</td></tr>"

                html = f"<table>{tr}</table>"

                print(html)

                from datetime import datetime
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")

                price_change_file = f"static/general/bolt_price_changes/price_changes_as_of_{formatted_datetime}.xlsx"
                spintex_stock_change_file = f"static/general/bolt_price_changes/spintex_stock_change_as_of_{formatted_datetime}.xlsx"
                osu_stock_change_file = f"static/general/bolt_price_changes/osu_stock_change_as_of_{formatted_datetime}.xlsx"
                nia_stock_change_file = f"static/general/bolt_price_changes/nia_stock_change_as_of_{formatted_datetime}.xlsx"

                worksheet.save(price_change_file)
                spintex_stock_book.save(spintex_stock_change_file)
                osu_stock_book.save(osu_stock_change_file)
                nia_stock_book.save(nia_stock_change_file)

                if send == 'yes':
                    if price_count > 0 or spintex_count > 0 or nia_count > 0 or osu_count > 0:
                        Emails(sent_to="solomon@snedaghana.com", subject='BOLT UPDATE', body=html,
                               attachments=f"{price_change_file},{spintex_stock_change_file},"
                                           f"{osu_stock_change_file},{nia_stock_change_file}").save()

                success_response['message'] = {
                    'price_change': {
                        'file': price_change_file,
                        'count': sheet_row - 2
                    },
                    'spintex_stock_change': {
                        'file': spintex_stock_change_file,
                        'count': spintex_stock_row - 2
                    },
                    'osu_stock_change_file': {
                        'file': osu_stock_change_file,
                        'count': osu_stock_row - 2
                    },
                    'nia_stock_change_file': {
                        'file': nia_stock_change_file,
                        'count': nia_stock_row - 2
                    }
                }

            elif module == 'export_items':
                key = data.get('key')
                format = data.get('format')
                if key == '*':
                    items = BoltItems.objects.all()
                    file_name = f"static/general/bolt/bolt-items.xlsx"
                else:
                    items = BoltItems.objects.filter(group_id=key)
                    group = BoltGroups.objects.get(pk=key)
                    file_name = f"static/general/bolt/{group.name}.xlsx"

                import openpyxl
                workbook = openpyxl.Workbook()
                sheet = workbook.active

                if format == 'excel':

                    sheet['A1'] = "BARCODE"
                    sheet['B1'] = "NAME"
                    sheet['C1'] = "PRICE"
                    sheet['D1'] = "SPINTEX"
                    sheet['E1'] = "NIA"
                    sheet['F1'] = "OSU"
                    row = 2

                    for item in items:
                        sheet[f'A{row}'] = item.barcode
                        sheet[f'B{row}'] = item.item_des
                        sheet[f'C{row}'] = item.price
                        sheet[f'D{row}'] = item.stock_spintex
                        sheet[f'E{row}'] = item.stock_nia
                        sheet[f'F{row}'] = item.stock_osu
                        row += 1

                    workbook.save(file_name)
                    success_response['message'] = file_name

        elif method == 'PATCH':
            if module == 'price_update':
                items = BoltItems.objects.all()

                for item in items:
                    item.price = item.inv_price
                    item.save()

        response = success_response

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response)
