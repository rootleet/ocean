class Cmms {
    carMaintainanceLog(carNumber) {

        let data = {
            "menu": {
                "header": "carjob",
                "data": {
                    "carno": carNumber,
                    "records": 5
                }
            }
        }
        return apiv2('cmms', 'null', data)

    }

    carJob(carNumber) {

        let response = cmms.carMaintainanceLog(carNumber)
        if (isJson(response)) {
            let resp = JSON.parse(response);
            let status, message
            status = resp['status']

            if (status === 200) {
                // positive response
                message = resp['message']

                let customer, asset, wos, woc
                customer = message['customer']
                asset = message['asset'];
                wos = message['jobs']
                woc = wos['count']

                // load header
                let car_detail = `<table class="table-sm">
                                <tr>
                                    <td>Name : </td><td>${asset['name']}</td>
                                </tr>
                                <tr>
                                    <td>Car N<u>0</u> : </td><td>${asset['asset_no']}</td>
                                </tr>
                                <tr>
                                    <td>Chassis : </td><td>${asset['chassis']}</td>
                                </tr>
                            </table>`
                $('#assetBody').html(car_detail)

                let cust_detail = `<table class="table-sm">
                                <tr>
                                    <td>Name : </td><td>${customer['name']}</td>
                                </tr>
                                <tr>
                                    <td>Contact : </td><td>${customer['contact']}</td>
                                </tr>
                            </table>`
                $('#custBody').html(cust_detail)

                // al('success',"LOAD HEADER")

                let wotr = ''
                if (woc > 0) {
                    // load trans

                    let wor = wos['records']
                    for (let w = 0; w < wor.length; w++) {
                        let wo = wor[w]
                        wotr += `<tr>
                                <td>${wo['wreq_no']}</td>
                                <td>${wo['wo_no']}</td>
                                <td>${wo['invoice_entry']}</td>
                                <td>${wo['wo_date']}</td>
                            </tr>`
                    }
                } else {
                    wotr = "NO WO TRANS"
                }
                $('#tbody').html(wotr)
                $('#carFollups').show()


            } else {
                al('info', resp['message'])
            }

            ctable(resp)
        } else {
            swal_response("There is an error retrieving car job")
        }

    }

    carFollowUps(carNumber) {
        let data = {
            "menu": {
                "header": "followup",
                "data": {
                    "carno": carNumber,
                    "records": 5
                }
            }
        }

        return apiv2('cmms', 'none', data)
    }

    SaveFollowup() {
        let carno = $('#searchQuery').val()
        if (carno.length > 0) {
            let title, message
            title = $('#ftitle').val();
            message = $('#freply').val();

            if (title.length < 1) {
                al('error', "Please provide feedback title")
            } else if (message.length < 1) {
                al('error', "Please provide feedback response")
            } else {

                // save
                let data = {
                    "menu": {
                        "header": "newfollowup",
                        "data": {
                            "carno": carno,
                            "title": title,
                            "message": message,
                            "owner": 1
                        }
                    }
                }

                apiv2('cmms', 'null', data)
                cmms.carFollowUps(carno)
                $('#newFolloup').modal('hide')
                al('success', "Response logged")

            }



        }
    }

    async groupTax(carNumber) {
        const data = {
            menu: {
                header: 'taxUpdate',
                data: {},
            },
        };

        try {
            const resp = apiv2('cmms', 'null', data);
            $('#loader').modal('hide');
            if (isJson(JSON.stringify(resp))) {
                const r = JSON.parse(resp);
                al('info', r.message);
            } else {
                al('error', 'INVALID RESPONSE RESPONSE');
            }
        } catch (error) {
            console.error(error);
            al('error', 'An error occurred while processing the request.');
        }
    }

    // stock take
    stockCount() {
        let myName = $('#myName').val()

        // validate quantity and item ref
        let qty, item_ref
        qty = $('#take_qty').val()
        item_ref = $('#item_ref').val()

        if (qty.length < 1 || item_ref.length < 1) {
            alert("Quantity or Item Ref should enter")
        } else {
            // make payload
            let payload = {
                "module": "stock",
                "data": {
                    "stage": "tran",
                    "item_ref": item_ref,
                    "qty": qty,
                    'user': myName
                }
            }


            let call = api.call('PUT', payload, '/cmms/api/')
            // let status,status_code,message
            alert(call['message'])

            cmms.stockPreview()

        }
    }

    // preview stock
    stockPreview() {
        let payload = {
            "module": "stock",
            "data": {
                "stage": "active"
            }
        }

        let response = api.call('VIEW', payload, '/cmms/api/')
        let tr = ''
        if (response['status_code'] === 200) {
            let count, trans
            count = response['message']['count']
            trans = response['message']['trans']

            if (count > 0) {
                // loo trans
                for (let index = 0; index < trans.length; index++) {
                    let tran = trans[index];
                    let barcode, name, quantity, owner, price, value
                    barcode = tran['barcode']
                    name = tran['name']
                    quantity = tran['quantity']
                    owner = tran['owner']
                    value = tran['value']
                    price = tran['price']
                    tr += `<tr>
                    <td><small>${barcode}</small></td>
                    <td><small>${name}</small></td>
                    <td><small>${quantity}</small></td>
                    <td><small>${price}</small></td>
                    <td><small>${value}</small></td>
                    <td><small>${owner}</small></td>
                    </tr>`

                }
            }
        }
        $('#tbody').html(tr)
    }

    stockFind() {
        let barcode = $('#stock_add_barcode').val()

        // validate barcode
        if (barcode.length > 0) {
            // get item details
            let payload = {
                "module": "product",
                "data": {
                    "range": "single",
                    "barcode": barcode
                }
            }



            // api call
            let response = api.call('VIEW', payload, '/cmms/api/')
            let status, status_code, message

            status = response['status']
            status_code = response['status_code']
            message = response['message']

            if (status_code === 200) {
                let count, trans
                count = message['count']

                // there is positive resposne
                if (count === 1) {
                    // there is product as expected
                    trans = message['trans'][0]
                    let name, item_ref
                    name = trans['name']
                    item_ref = trans['item_ref']

                    // add item
                    Swal.fire({
                        'title': 'STOCK RECORD',
                        showConfirmButton: false,
                        'html': `<div style='text-align:left'><strong>BARCODE</strong> : <small class='text-info'>${barcode}</small><br><strong>NAME</strong> : <small class='text-info'>${name}</small></div>
                        <hr><input id='item_ref' value='${item_ref}' class='form-control mb-2' readonly>
                        <input min='1' id='take_qty' class='form-control mb-2' type='number'>
                        <button onclick='cmms.stockCount()' class='btn btn-success w-100'>ADD</button>`
                    });

                    // let tr = `<tr><td><small>${barcode}</small></td><td><small>${name}</small></td><td><small>10</small></td></tr>`

                    // $('#tbody').prepend(tr)

                } else {
                    alert(`NO PRODUCT FOUND (${count})`)
                }
            } else {
                alert(message)
            }


        } else {
            alert("BARCODE SHOULD ENTER")
        }
    }

    // locations
    locationMaster() {
        let payload = {
            'module': "system",
            'data': {
                'task': 'get_locations'
            }
        }

        let response = api.call('VIEW', payload, '/cmms/api/')
        if (response['status_code'] === 200) {
            // there is response
            let message, count, trans
            message = response['message']
            count = message['count']
            trans = message['trans']
            return message
        }

    }

    // new stock
    newStock() {
        Swal.fire({
            title: 'OPEN STOCK TAKE',
            html:
                '<input id="location" class="swal2-input" placeholder="Location">' +
                '<input id="remark" class="swal2-input" placeholder="Remark">',
            focusConfirm: false,
            preConfirm: () => {
                const loc = $('#location').val();
                const remark = $('#remark').val();

                if (!loc || !remark) {
                    Swal.showValidationMessage('Please enter both Location and Remark');
                } else {
                    let payload = {
                        "module": "stock",
                        "data": {
                            "stage": "hd",
                            "loc": loc,
                            "remark": remark
                        }
                    };

                    let response = api.call('PUT', payload, '/cmms/api/');
                    console.table(response)
                    location.reload()
                    alert(response['message']);
                }
            }
        });
    }

    // close stock
    closeStock() {
        let payload = {
            'module': 'stock',
            'data': {
                'stage': 'hd',
                'task': 'close'
            }
        }
        let response = api.call('PATCH', payload, '/cmms/api/');

        alert(response['message'])
        location.reload()
    }

    // compare
    compare(pk) {
        let groups = cmms.productGroups()
        console.table(groups)
        let g_opt = ''
        if(groups['status_code'] === 200){
            let g_message,g_count,g_grps
            g_message = groups['message']
            g_grps = g_message['groups']
            g_count = g_message['counts']

            for (let i = 0; i < g_count; i++) {
                let el = g_grps[i]
                g_opt += `<option value="${el['code']}">${el['name']}</option>`
            }

        }
        Swal.fire({
      title: 'Select Date',
      html: `<select class="form-control w-50 mx-auto mb-2" id="preview">
                <option value="preview">PREVIEW</option>
                <option value="excel">EXCEL</option>
            </select><select class="form-control w-50 mx-auto mb-2" id="group">${g_opt}</select><input type="date" id="swal-date" class="swal2-input">`,
      showCancelButton: true,
      confirmButtonText: 'OK',
      preConfirm: () => {
        const selectedDate = $('#swal-date').val();
        const selectedGroup = $('#group').val()
        const preview = $('#preview').val()
        if (selectedDate === '') {
          Swal.showValidationMessage('Please select a date');
        }
        if (selectedGroup === '') {
          Swal.showValidationMessage('Please select Group');
        }
        return {
            'date':selectedDate,
            'group':selectedGroup,
            'preview':preview
        };
      }
    }).then((result) => {
      if (result.isConfirmed) {
          console.table(result)
        const selectedDate = result.value.date;
        const selectedGroup = result.value.group
        const selectPreview = result.value.preview
        const formattedDate = new Date(selectedDate).toISOString().split('T')[0];

        let payload = {
          "module": "stock",
          "data": {
              "stage":"export",
            "compare":"final_compare",
            "as_of":formattedDate,
            "doc":selectPreview,
            "pk":pk,
            "group":selectedGroup
          }
        };

        console.table(payload)

        let response = api.call('VIEW',payload,'/cmms/api/')
        // console.table(response)
        let message,trans,header
        let html = '';
        if(response['status_code'] === 200){
            if(selectPreview === 'preview'){

                message = response['message']
                trans = message['trans']
                header = message['header']
                let g_count,g_sys,g_dif,v_dif
                g_count = 0;g_sys=0;g_dif=0,v_dif=0
                $('#g_modal_title').html(`STOCK COMPARE as of ${formattedDate}<br><strong>LOC : </strong> ${header['location']} <br><strong>REMARKS : </strong> ${header['remark']}`)
                let tr = ''
                let counted,not_counted
                counted = trans['counted']
                not_counted = trans['not_counted']

                for (let c_index = 0; c_index < counted.length; c_index++) {
                    let element = counted[c_index];
                    let barcode,item_ref,name,count_qty,av_qty,qty_diff
                    barcode = element['barcode']
                    item_ref = element['item_ref']
                    name = element['desription']
                    count_qty = parseFloat(element['counted']).toFixed(2)
                    av_qty = parseFloat(element['av_qty']).toFixed(2)
                    qty_diff = parseFloat(element['qty_diff']).toFixed(2)
                    let diff_val = parseFloat(element['diff_val']).toFixed(2)

                    g_count += parseFloat(count_qty)
                    g_sys += parseFloat(av_qty)
                    g_dif += parseFloat(qty_diff)
                    v_dif += parseFloat(diff_val)

                    let text = ''
                    if(qty_diff < 0){
                        text = 'text-danger'
                    }


                    tr += `<tr class='${text}'>
                                <td><small><i class="bi-check-square"></i></small><td><small>${item_ref}</small></td><td><small>${barcode}</small></td><td><small>${name}</small></td><td><small>${count_qty}</small></td><td><small>${av_qty}</small></td><td><small>${qty_diff}</small></td>
                                <td><small>${diff_val}</small></td>
                            </tr>`


                }

                for (let n_index = 0; n_index < not_counted.length; n_index++) {
                    let element = not_counted[n_index];
                    let barcode,item_ref,name,count_qty,av_qty,qty_diff
                    barcode = element['barcode']
                    item_ref = element['item_ref']
                    name = element['desription']
                    count_qty = parseFloat(element['counted']).toFixed(2)
                    av_qty = parseFloat(element['av_qty']).toFixed(2)
                    qty_diff = parseFloat(element['qty_diff']).toFixed(2)
                    let diff_val = parseFloat(element['diff_val']).toFixed(2)

                    g_count += parseFloat(count_qty)
                    g_sys += parseFloat(av_qty)
                    g_dif += parseFloat(qty_diff)
                    v_dif += parseFloat(diff_val)

                    let text = ''
                    if(qty_diff < 0){
                        text = 'text-danger'
                    }


                    tr += `<tr class='${text}'>
                                <td><small><i class="bi-square"></i></small><td><small>${item_ref}</small></td><td><small>${barcode}</small></td><td><small>${name}</small></td><td><small>${count_qty}</small></td><td><small>${av_qty}</small></td><td><small>${qty_diff}</small></td>
                                <td><small>${diff_val}</small></td>
                           </tr>`


                }

                html = `<table class='table table-bordered table-sm table-responsive'>
                <thead>
                  <tr><th>CH</th><th>ITEM REF</th><th>BARCODE</th><th>DESCRIPTION</th><th>PHY</th><th>SYS</th><th>QTY DIFF</th><th>VAL DIFF</th></tr>
                </thead>
                <tbody class="dataTable">
                <tr class='text-primary'><td colspan='4'>SUMMARY</td><td><small>${g_count}</small></td><td><small>${g_sys}</small></td><td><small>${g_dif}</small></td><td><small>${v_dif.toFixed(2)}</small></td></tr>
                  ${tr}
                </tbody>
              </table>`
            }  else if (selectPreview === 'excel'){
                html = `<a target="_blank" href='${response['message']}'>DOWNLOAD FILE</a>`
            }

        } else {
            $('#g_modal_title').html("Download File")
            html = response['message']
        }

        // Rest of your code here
        $('#g_modal_size').addClass('modal-xl');
        $('#g_modal_body').html(html);
        $('#g_modal').modal('show');
        // Rest of your code here
      }
    });

        
       
    }

    // get groups
    productGroups(){
        let payload = {
            'module':'groups',
            'data':{}
        }

        return api.call('VIEW', payload, '/cmms/api/')

    }

}

const cmms = new Cmms()