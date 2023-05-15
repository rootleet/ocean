from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import json

from django.views.decorators.csrf import csrf_exempt

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


                response["status_code"] = 200
                response["status"] = "OK"

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
        elif method == "GET":
            try:
                module = body["module"]
                # code to handle GET request and fetch data
                response["status_code"] = 200
                response["status"] = "OK"
                response["message"] = "Data retrieved successfully"
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
