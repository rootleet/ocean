import pyodbc
from django.db.models import Sum

from admin_panel.models import Locations, ProductTrans
from inventory.models import GrnTran
from ocean.settings import DB_SERVER, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def cmm_connect():
    server = f"{DB_SERVER},{DB_PORT}"
    database = DB_NAME
    username = DB_USER
    password = DB_PASSWORD
    driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    return pyodbc.connect(connection_string)
    # return connection.cursor()


# get stick
def get_stock(prod_pk, legend=None):
    if legend is None:
        legend = {}
    locations = Locations.objects.filter()
    legend['count'] = locations.count()
    arr = []
    for location in locations:
        pk = location.pk

        # get stock sum
        if ProductTrans.objects.filter(pk=prod_pk,loc=location).aggregate(Sum('tran_qty'))['tran_qty__sum'] is None:
            qty = 0
        else:
            qty = ProductTrans.objects.filter(pk=prod_pk,loc=location).aggregate(Sum('tran_qty'))['tran_qty__sum']

        arr.append({'loc_id': location.code, 'loc_desc': location.descr, 'stock': qty})

    legend['trans'] = arr
    return legend


def suppler_details(prod_id, legend=None):
    if legend is None:
        legend = {}
    grns = GrnTran.objects.filter(product_id=prod_id)
    if grns.count() > 0:
        grn = grns.last()
        legend['supplier'] = grn.entry_no.supplier.company,
        legend['last_rec_price'] = grn.un_cost
        legend['last_rec_date'] = grn.entry_no.created_on
    else:
        legend['supplier'] = 'NONE',
        legend['last_rec_price'] = 0
        legend['last_rec_date'] = 'NONE'

    return legend


def cardex(prod_id, legend=None):
    if legend is None:
        legend = []

    trans = ProductTrans.objects.filter(product_id=prod_id)
    for tran in trans:
        legend.append(
            {
                'date': tran.created_on,
                'doc_type': tran.doc,
                'entry_no': tran.doc_ref,
                'loc_id': tran.loc.code,
                'loc_desc': tran.loc.descr,
                'qty': tran.tran_qty
            }
        )

    return legend
