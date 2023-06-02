import hashlib

from django.contrib.auth.models import User
from django.contrib.messages.context_processors import messages
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import json

from django.views.decorators.csrf import csrf_exempt

from admin_panel.models import TicketHd, SmsApi, Sms
from appscenter.models import AppsGroup, App, AppAssign, VersionControl
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
                            message=f"There is an issue with title '{title}' reported by {own.username}").save()

                        response['message'] = "Ticked Reported"

                        response["status_code"] = 200
                        response["status"] = "OK"

                    except  Exception as e:
                        response['message'] = str(e)

                        response["status_code"] = 500
                        response["status"] = "error"

                elif module == 'appcenter':
                    task = data.get('task')

                    if task == 'newgrp':
                        # save new app group
                        name = data.get('name')

                        from datetime import datetime

                        # Get the current time
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Concatenate the current time and the variable
                        data_to_hash = current_time + name

                        # Create an MD5 hash object
                        md5_hash = hashlib.md5()

                        # Update the hash object with the data to be hashed
                        md5_hash.update(data_to_hash.encode('utf-8'))

                        # Generate the MD5 hash
                        uni = md5_hash.hexdigest()

                        if AppsGroup.objects.filter(name=name).exists():
                            response['status_code'] = 200
                            response['status'] = "exist"
                            response['message'] = "Group Already Exist"
                        else:
                            AppsGroup(name=name, uni=uni).save()
                            response['status_code'] = 202
                            response['status'] = "success"
                            response['message'] = "Group Added"

                    elif task == 'assign':
                        app = data.get('app')
                        mach = data.get('mach')

                        app_count = App.objects.filter(pk=app).count()
                        mach_count = Computer.objects.filter(mac_address=mach).count()

                        if app_count != 1:
                            response['status_code'] = 404
                            response['status'] = 'not found'
                            response['message'] = "Application Not Found"
                        elif mach_count != 1:
                            response['status_code'] = 404
                            response['status'] = 'not found'
                            response['message'] = "PC Not Found"
                        else:

                            # insert into assign
                            app_f = App.objects.get(pk=app)
                            mach_f = Computer.objects.get(mac_address=mach)

                            # check if pc pc app exist
                            if AppAssign.objects.filter(app=app_f, mach=mach_f).exists():
                                response['status_code'] = 200
                                response['status'] = 'success'
                                response['message'] = "App already assigned to PC"
                            else:
                                AppAssign(app=app_f, mach=mach_f).save()

                                response['status_code'] = 202
                                response['status'] = 'success'
                                response['message'] = "App Assigned"


            except KeyError as e:
                response["status_code"] = 400
                response["status"] = "Bad Request"
                response["message"] = f"Missing required field: {e.args[0]}"
        elif method == "PATCH":
            try:
                module = body["module"]
                data = body["data"]
                # code to handle PATCH request and update data
                if module == 'appcenter':
                    task = data.get('task')
                    if task == 'mark_update':
                        mac = data.get('mac')
                        app = data.get('app')

                        try:
                            pc = Computer.objects.get(mac_address=mac)
                            application = App.objects.get(pk=app)

                            assignment, created = AppAssign.objects.get_or_create(app=application, mach=pc)
                            assignment.version = application.version
                            assignment.save()
                            response['message'] = "Update history updated"
                        except Exception as e:
                            response['status_code'] = 404
                            response['message'] = f"COULD NOT UPDATE ASSIGN {str(e)}"
                    else:
                        response['message'] = 'no task'

            except KeyError as e:
                response["status_code"] = 400
                response["status"] = "Bad Request"
                response["message"] = f"Missing required field: {e.args[0]}"

        elif method == "DELETE":
            try:
                module = body["module"]
                # code to handle DELETE request and delete data
                if module == 'appcenter':
                    task = data.get('task')
                    if task == 'delgrp':
                        pk = data.get('pk')
                        AppsGroup.objects.get(pk=pk).delete()

                    elif task == 'delapp':
                        pk = data.get('pk')
                        App.objects.get(pk=pk).delete()

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

                elif module == 'appcenter':
                    task = data.get('task')
                    pk = data.get('pk')
                    arr = []
                    if task == 'grp':

                        if pk == '*':
                            grps = AppsGroup.objects.all()
                        else:
                            grps = AppsGroup.objects.filter(pk=pk)

                        for grp in grps:
                            name = grp.name
                            uni = grp.uni

                            arr.append({'name': name, 'uni': uni, 'pk': grp.pk})

                    elif task == 'app':
                        if pk == '*':
                            apps = App.objects.all()
                        else:
                            apps = App.objects.filter(pk=pk)

                        for app in apps:
                            name = app.name
                            uni = app.uni

                            arr.append({
                                'name': name,
                                'uni': uni,
                                'pk': app.pk,
                                'icon': app.icon.url,
                                'root': app.root,
                                'version': app.version,
                                'group': {
                                    'name': app.group.name
                                }
                            })

                    elif task == 'update':
                        mach_addr = data.get('mac')

                        # check all my apps and updates
                        if Computer.objects.filter(mac_address=mach_addr).count() == 1:
                            pc = Computer.objects.get(mac_address=mach_addr)
                            # check apps for pc
                            myapps = AppAssign.objects.filter(mach=pc)
                            for apps in myapps:

                                app = apps.app
                                app_ver = app.version
                                app_root = app.root

                                my_ver = apps.version

                                if app_ver > my_ver:
                                    # get update
                                    update = VersionControl.objects.get(app=app, version_no=app_ver)
                                    obj = {
                                        'apppk':app.pk,
                                        'name': app.name,
                                        'update': 'Y',
                                        'file': update.files.url,
                                        'root': app_root, 'app_ver': app_ver, 'my_ver': my_ver
                                    }
                                    arr.append(obj)
                                else:
                                    arr.append(
                                        {'update': 'N', 'app_ver': app_ver, 'my_ver': my_ver, 'name': app.name, })

                                pass
                        else:
                            response['status_code'] = 404
                            response['status'] = 'ok'
                            response['message'] = "Device not found"
                    response['message'] = arr



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
