import json
import sys
from http.client import responses

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import Locations, TransferHD, TransferTran, ProductMaster
from admin_panel.views import bank_posts
from retail.models import Products


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

    error_response = {
        'status_code': 505,
        'message': "Procedure Failed"
    }

    # get method
    method = request.method

    try:

        body = json.loads(request.body)
        module = body.get('module')
        data = body.get('data')

        if method == 'PUT':
            if module == 'product':
                pass

            elif module == 'transfer':
                header = data.get("header")
                transactions = data.get("transactions")
                mypk = header.get('mypk')
                owner = User.objects.get(pk=mypk)

                l_from = header.get('loc_from')
                l_to = header.get('loc_to')

                loc_from = Locations.objects.get(pk=l_from)
                loc_to = Locations.objects.get(pk=l_to)
                remarks = header.get("remarks")

                entry_no = f"TR{loc_from.code}{TransferHD.objects.filter(loc_fr=loc_from).count() + 1}"

                try:
                    TransferHD(
                        entry_no=entry_no,loc_fr=loc_from,remarks=remarks,loc_to=loc_to,created_by=owner
                    ).save()
                    thd = TransferHD.objects.get(entry_no=entry_no)
                    line = 1
                    for tr in transactions:
                        print(tr)
                        TransferTran(
                            parent=thd,
                            line = line,
                            product = ProductMaster.objects.get(barcode=tr['barcode']),
                            packing = tr['packing'],
                            pack_qty = tr['pack_qty'],
                            tran_qty = tr['tran_qty'],
                            unit_cost = tr['unit_cost'],
                            cost = tr['total_cost'],
                        ).save()
                        line += 1
                    success_response['message'] = f"Transfer Saved {entry_no}"
                    response = success_response
                except Exception as e:
                    TransferHD.objects.filter(entry_no=entry_no).delete()
                    error_response['message'] = f"Transfer Failed: {e}"
                    response = error_response

        elif method == 'VIEW':
            # view transfer in window
            arr = []
            if module == 'transfer':
                doc = data.get("doc")
                pk = data.get("pk")

                hds = TransferHD.objects.filter(pk=pk)
                for hd in hds:
                    obj = {
                        "header":hd.obj()
                    }

                    # get transactions
                    trans = []
                    transactions = TransferTran.objects.filter(parent=hd)
                    for tran in transactions:
                        trans.append(tran.obj())

                    obj['transactions'] = trans
                    arr.append(obj)

                success_response['message'] = arr
                response = success_response
                print(responses)

        elif method == 'PATCH':
            if module == 'transfer':
                header = data.get("header")

                transactions = data.get("transactions")
                mypk = header.get('mypk')
                owner = User.objects.get(pk=mypk)

                l_from = header.get('loc_from')
                l_to = header.get('loc_to')

                loc_from = Locations.objects.get(pk=l_from)
                loc_to = Locations.objects.get(pk=l_to)
                remarks = header.get("remarks")

                entry_no = header.get('entry_no')

                try:

                    thd = TransferHD.objects.get(entry_no=entry_no)
                    thd.remarks = remarks
                    thd.loc_fr = loc_from
                    thd.loc_to = loc_to
                    line = 1
                    # delete transactions
                    TransferTran.objects.filter(parent=thd).delete()
                    for tr in transactions:
                        print(tr)
                        TransferTran(
                            parent=thd,
                            line = line,
                            product = ProductMaster.objects.get(barcode=tr['barcode']),
                            packing = tr['packing'],
                            pack_qty = tr['pack_qty'],
                            tran_qty = tr['tran_qty'],
                            unit_cost = tr['unit_cost'],
                            cost = tr['total_cost'],
                        ).save()
                        line += 1
                    thd.save()
                    success_response['message'] = f"Transfer Saved {entry_no}"
                    response = success_response
                except Exception as e:
                    # TransferHD.objects.filter(entry_no=entry_no).delete()
                    error_response['message'] = f"Transfer Failed: {e}"
                    response = error_response

            elif module == 'send_transfer':
                entry_no = data.get('entry_no')
                my_pk = data.get('mypk')
                delivery_by = data.get('delivery_by')

                print(data)

                transfer = TransferHD.objects.get(entry_no = entry_no)
                transfer.is_sent = True
                transfer.sent_by = User.objects.get(pk=my_pk)
                transfer.delivery_by = delivery_by
                transfer.save()

                response = success_response

        else:
            error_response['message'] = f"Method Not Allowed: {method}"
            response = error_response

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response, safe=False)