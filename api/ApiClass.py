from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse

from inventory.models import PoHd, PoTran, DocAppr

response = {
    'status': 505,
    'message': "No Module "
}


def GetPo(entry):
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
                tran_pac = transaction.packing
                packing = {
                    'code':tran_pac.packing_un.code,
                    'descr':tran_pac.packing_un.descr,
                    'pack_un_qty':tran_pac.pack_qty,
                    'tran_pack_qty':transaction.pack_qty
                }
                this_trans = {
                    'line': transaction.line,
                    'product_descr': transaction.product.descr,
                    'product_barcode': transaction.product.barcode,
                    'packing': packing,
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

        # status
        p_status = {
            'p_status': {
                'status': hd.status,
                'approved_by': 'PENDING',
                'approved_date': '',
                'approved_time': ''
            }
        }


        if hd.status == 1:
            appr = DocAppr.objects.get(doc_type='po', entry_no=hd.pk)
            # get approve details
            p_status['p_status']['approved_by'] = appr.approved_by.first_name
            p_status['p_status']['approved_date'] = appr.approved_on.date()
            # p_status['p_status']['approved_time'] = hd.approved_time

        meg.update(header)
        meg.update(trans)
        meg.update(nav)
        meg.update(cost)
        meg.update(p_status)

        response['status'] = 200
        response['message'] = meg

    else:
        # if no po, return 404 and response message
        response['status'] = 404
        response['message'] = "Po Entry Not Found"

    return response


class ApiClass:
    pass
