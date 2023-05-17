from django.contrib.auth.models import User
from django.contrib.messages.context_processors import messages
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import json

from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import TicketHd, SmsApi, Sms
from inventory.models import Computer


@csrf_exempt
def api_function(request):
    method = request.method
    response = {"status_code": "", "status": "", "message": ""}

    try:
        body = json.loads(request.body)
        module = body.get('module')
        data = body.get('data')
    except json.JSONDecodeError as e:
        response["status_code"] = 400
        response["status"] = "Bad Request"
        response["message"] = f"Error decoding JSON: {e.msg}"
        return JsonResponse(response)

    try:

        if method == "PUT":
            try:
                module = body["module"]
                data = body["data"]

                # code to handle PUT request and update data
                if module == 'dev_mgmt':
                    # save device
                    ram = data.get('ram')
                    cpu = data.get('cpu')
                    storage = data.get('storage')
                    network = data.get('network')
                    system = data.get('system')
                    printer = data.get('printer')
                    ram_type = data.get('ram').get('ram_type')
                    ram_size = data.get('ram').get('ram_size')
                    cpu = data.get('cpu').get('cpu')
                    storage_type = data.get('storage').get('storage_type')
                    storage_size = data.get('storage').get('storage_size')
                    used_storage = data.get('storage').get('used_storage')
                    remaining_storage = data.get('storage').get('remaining_storage')
                    ip_address = data.get('network').get('ip_address')
                    mac_address = data.get('network').get('mac_address')
                    manufacturer = data.get('system').get('manufacturer')
                    model = data.get('system').get('model')
                    os = data.get('system').get('os')
                    sku = data.get('system').get('sku')
                    computer_name = data.get('system').get('computer_name')
                    logged_on_user = data.get('system').get('logged_on_user')
                    printer = data.get('printer')

                    # check if record with mac address exists in database
                    try:
                        computer = Computer.objects.get(mac_address=mac_address)
                        response["message"] = "Device updated successfully"
                    except Computer.DoesNotExist:
                        computer = Computer(mac_address=mac_address)
                        response["message"] = "Device added successfully"

                    # update or create new record
                    computer.ram_type = ram_type
                    computer.ram_size = ram_size
                    computer.cpu = cpu
                    computer.storage_type = storage_type
                    computer.storage_size = storage_size
                    computer.used_storage = used_storage
                    computer.remaining_storage = remaining_storage
                    computer.ip_address = ip_address
                    computer.manufacturer = manufacturer
                    computer.model = model
                    computer.os = os
                    computer.sku = sku
                    computer.printer = printer
                    computer.logged_on_user = logged_on_user
                    computer.computer_name = computer_name
                    computer.save()

                elif module == 'ticket':
                    owner = data.get('owner')
                    title = data.get('title')
                    descr = data.get('descr')



                    try:
                        own = User.objects.get(pk=owner)
                        TicketHd(title=title, descr=descr, owner=own).save()
                        # sms
                        smsapi = SmsApi.objects.get(is_default=1)
                        Sms(api=smsapi, to='0201998184',
                            message=f"There is an issue with title {title} reported by {own.username}").save()

                        response['message'] = "Ticked Reported"

                        response["status_code"] = 200
                        response["status"] = "OK"

                    except  Exception as e:
                        response['message'] = str(e)

                        response["status_code"] = 500
                        response["status"] = "error"



            except KeyError as e:
                response["status_code"] = 400
                response["status"] = "Bad Request"
                response["message"] = f"Missing required field: {e.args[0]}"
        elif method == "PATCH":
            try:
                module = body["module"]
                data = body["data"]
                # code to handle PATCH request and update data
                response["status_code"] = 200
                response["status"] = "OK"
                response["message"] = "Data updated successfully"
            except KeyError as e:
                response["status_code"] = 400
                response["status"] = "Bad Request"
                response["message"] = f"Missing required field: {e.args[0]}"
        elif method == "DELETE":
            try:
                module = body["module"]
                # code to handle DELETE request and delete data
                response["status_code"] = 200
                response["status"] = "OK"
                response["message"] = "Data deleted successfully"
            except KeyError as e:
                response["status_code"] = 400
                response["status"] = "Bad Request"
                response["message"] = f"Missing required field: {e.args[0]}"
        elif method == "VIEW":
            try:
                module = body["module"]
                response["status_code"] = 200
                response["status"] = "OK"
                response["message"] = "Data retrieved successfully"
                # code to handle GET request and fetch data
                if module == 'dev_mgmt':
                    frame = {
                        'count': 0,
                        'devices': []
                    }
                    devs = []
                    pk = data.get('pk')
                    if pk == '*':
                        devices = Computer.objects.filter(id__gt=0)
                    else:
                        devices = Computer.objects.filter(pk=pk)
                    frame['count'] = devices.count()
                    for device in devices:
                        # Loop through each item in the list
                        printers = device.printer.replace('[', '').replace(']', '').split(',')
                        printer_list = []
                        for printer in printers:
                            printer_list.append(printer.replace("'", '').strip())
                        computer = {
                            'ram': {
                                "ram_type": device.ram_type,
                                "ram_size": device.ram_size
                            },
                            "cpu": device.cpu,
                            'storage': {
                                'type': device.storage_type,
                                'size': device.storage_size,
                                'used': device.used_storage,
                                'remaining': device.remaining_storage
                            },
                            'network': {
                                'ip_address': device.ip_address,
                                'mac_address': device.mac_address
                            },
                            'system': {
                                'computer_name': device.computer_name,
                                'logged_on_user': device.logged_on_user,
                                "manufacturer": device.manufacturer,
                                "model": device.model,
                                "os": device.os,
                                "sku": device.sku,
                            },
                            'printers': printer_list
                        }

                        devs.append(computer)

                    frame['devices'] = devs

                    response['message'] = frame

            except KeyError as e:
                response["status_code"] = 400
                response["status"] = "Bad Request"
                response["message"] = f"Missing required field: {e.args[0]}"

        else:
            response["status_code"] = 405
            response["status"] = "Method Not Allowed"
            response["message"] = f"Invalid HTTP method: {method}"

    except Exception as e:
        response["status_code"] = 400
        response["status"] = "Error"
        response["message"] = f"{e}"

    return JsonResponse(response)
