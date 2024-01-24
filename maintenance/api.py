import json
import sys

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from admin_panel.anton import new_sms
from maintenance.models import Maintenance, MaintenanceHistory, MaintenanceAssetGroup, MaintenanceAssetSubGroup, \
    MaintenanceAsset


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

        if method == 'PUT':
            if module == 'maintenance_asset_group':
                name = data.get('name')
                user_pk = data.get('mypk')
                owner = User.objects.get(pk=user_pk)
                MaintenanceAssetGroup(name=name, owner=owner).save()
                success_response['message'] = "Asset Group Created Successfully"

            elif module == 'maintenance_asset_sub_group':
                name = data.get('name')
                user_pk = data.get('user_pk')
                group_pk = data.get('group_pk')
                group = MaintenanceAssetGroup.objects.get(pk=group_pk)
                owner = User.objects.get(pk=user_pk)
                MaintenanceAssetSubGroup(group=group, owner=owner, name=name).save()
                success_response['message'] = "Asset SubGroup Created Successfully"

            elif module == 'maintenance_asset':
                sku = data.get('sku')
                group_pk = data.get('group')
                sub_group_pk = data.get('sub_group')
                group = MaintenanceAssetGroup.objects.get(pk=group_pk)
                subgroup = MaintenanceAssetSubGroup.objects.get(pk=sub_group_pk)
                user_pk = body.get('user_pk')
                owner = User.objects.get(pk=user_pk)

                MaintenanceAsset(sku=sku, group=group, subgroup=subgroup, owner=owner).save()
                success_response['message'] = "Asset Created Successfully"


            elif module == 'maintenance_request':
                title = data.get('title')
                description = data.get('description')
                mypk = data.get('mypk')
                owner = User.objects.get(pk=mypk)

                maintenance = Maintenance(title=title, description=description, owner=owner)
                maintenance.save()
                sms_message = (f"NEW MAINTENANCE REQUEST\n\nTitle: {title}\n\nDescription: Sent Via Email or in "
                               f"ocean\n\nOwner: {owner.get_full_name()}")
                new_sms('0546310011', sms_message)
                success_response['message'] = "Service Logged"

            elif module == 'maintenance_log':
                maintenance = data.get('maintenance')
                mypk = data.get('mypk')
                title = data.get('title')
                description = data.get('description')

                # get objects
                main = Maintenance.objects.get(pk=maintenance)
                owner = User.objects.get(pk=mypk)

                # add to history
                history = MaintenanceHistory(maintenance=main, owner=owner, description=description, title=title)
                history.save()
                success_response['message'] = "Record Updated"

        elif method == 'VIEW':
            arr = []
            if module == 'maintenance_asset_group':
                key = data.get('key', '*')
                if key == '*':
                    asset_groups = MaintenanceAssetGroup.objects.all()
                else:
                    asset_groups = MaintenanceAssetGroup.objects.filter(pk=key)

                # loop through assets objects
                for asset_group in asset_groups:
                    subgroups = asset_group.subgroups()
                    sg = []
                    for subgroup in subgroups:
                        sg.append({
                            'name': subgroup.name,
                            'pk': subgroup.pk
                        })
                    arr.append({
                            'pk': asset_group.pk,
                            'name': asset_group.name,
                            'is_active': asset_group.is_active,
                            'owner': {
                                'name': asset_group.owner.get_full_name(),
                                'username': asset_group.owner.username,
                                'pk': asset_group.owner.pk
                            },
                            'timestamp': {
                                'created_on': asset_group.created_on,
                                'modified_on': asset_group.modified_on
                            },
                            'subgroups': sg
                        })

                success_response['message'] = arr


            elif module == 'maintenance_asset_sub_group':
                key = data.get('key', '*')
                if key == '*':
                    asset_sub_groups = MaintenanceAssetGroup.objects.all()
                else:
                    asset_sub_groups = MaintenanceAssetGroup.objects.filter(pk=key)

                for subgroup in asset_sub_groups:
                    arr.append(
                        {
                            'name': subgroup.name,
                            'pk': subgroup.pk
                        }
                    )

            elif module == 'maintenance_asset':
                key = data.get('key', '*')
                assets = MaintenanceAsset.objects.all()
                if key != '*':
                    assets = MaintenanceAsset.objects.filter(pk=key)

                for asset in assets:
                    arr.append({
                        'sku': asset.sku,
                        'pk': assets.pk,
                        'name': asset.name,
                        'group': {
                            'name': asset.group.name,
                            'pk': asset.group.pk
                        },
                        'subgroup': {
                            'pk': asset.subgroup.pk,
                            'name': asset.subgroup.name
                        },
                        'owner': asset.owner.get_fullname(),
                        'created_on': asset.created_on,
                        'image': asset.image_link()
                    })

        elif method == 'PATCH':
            if module == 'close':
                maintenance = data.get('maintenance')
                mypk = data.get('mypk')
                message = data.get('message')
                main = Maintenance.objects.get(pk=maintenance)

                owner = User.objects.get(pk=mypk)
                history = MaintenanceHistory(title='CLOSING', description=message, owner=owner, maintenance=main)

                main.is_open = 2
                history.save()
                main.save()

                success_response['message'] = "Record Closed"

        response = success_response

    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response, safe=False)
