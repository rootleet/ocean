class CmmsCust {
    getServiceCustomerAssets(code){

        let payload = {
            "module":"cust_asset",
            "data":{
                "customer":code
            }
        }

        return api.call('VIEW',payload,'/cmms/api/')

    }

    getInvoice(invoice){
        let payload = {
            "module":"invoice_detail",
            "data":{
                "invoice":invoice
            }
        }

        return api.call('VIEW',payload,'/cmms/api/')
    }

    invoicePreview(invoice){
        let response = cmms_cust.getInvoice(invoice)

        if (response['status_code'] === 200){
            let message = response['message']
            let header,asset,trans;
            trans = message['trans']
            asset = message['asset']
            header = message['header']

            let bb_cust_code = asset['owner']
            let asset_code = asset['code']
            let customer = cmms_cust.getCustomer(bb_cust_code)['message']

            console.log(bb_cust_code)
            let tr = ''
            if(trans.length > 0){
                let count = trans.length;
                for (let inn = 0; inn < count; inn++) {
                    let inv = trans[inn]
                    tr += `
                        <tr>
                            <td>${inv['type']}</td>
                            <td>${inv['name']}</td>
                            <td>${inv['packing']}</td>
                            <td>${inv['unit_qty']}</td>
                            <td>${inv['unit_price']}</td>
                            <td>${inv['net']}</td>
                            <td>${inv['tax']}</td>
                            <td>${inv['gross']}</td>
                 
                        </tr>
                    `
                }

                let tab = `
                    <button onclick="cmms_cust.viewAssetServiceHistory('${asset_code}','${bb_cust_code}')" class="btn btn-info">INVOICES</button>
                    <hr>
                        <div class="container">
                            <div class="row d-flex flex-wrap justify-content-between">
                                <div class="col-sm-5">
                                    <div class="card">
                                        <div class="card-header"><strong class="card-title">ASSET DETAILS</strong></div>
                                        <div class="card-body p-2">
                                            <table class="table table-sm table-bordered">
                                                <tr><td>NUMBER</td><td>${asset['number']}</td></tr>
                                                <tr><td>CHASIS</td><td>${asset['chassis']}</td></tr>
                                                <tr><td>MODEL</td><td>${asset['model']}</td></tr>
                                            </table>
                                        </div>
                                    </div>
                                    
                                    
                                </div>
                                
                                <div class="col-sm-5">
                                    <div class="card">
                                        <div class="card-header"><strong class="card-title">CUSTOMER DETAILS</strong></div>
                                        <div class="card-body p-2">
                                            <table class="table table-sm table-bordered">
                                                <tr><td>NAME</td><td>${customer['name']}</td></tr>
                                                <tr><td>PHONE</td><td>${customer['phone']}</td></tr>
                                                <tr><td>EMAIL</td><td>${customer['email']}</td></tr>
                                            </table>
                                        </div>
                                    </div>
                                    
                                    
                                </div>
                                
                            </div>
                        </div>
                    <hr>
                    <table class="table table-sm table-bordered">
                        <thead><tr><th>TYPE</th><th>NAME</th><th>PACKING</th><th>QUANTITY</th><th>PRICE</th><th>NET</th><th>TAX</th><th>GROSS</th></tr></thead>
                        <tbody>${tr}<tr><td colspan="5">SUMMARY</td><td>${parseFloat(header['net']).toFixed(2)}</td><td>${parseFloat(header['tax']).toFixed(3)}</td><td>${parseFloat(header['gross']).toFixed(3)}</td></tr></tbody>
                    </table>
                    
                `

                $('#g_modal_title').text("INVOICE DETAIL")
                $('#g_modal_body').html(tab)

            } else {
                kasa.info("No INVOICE TRANSACTION")
            }

        } else if(response['status_code'] !== 200) {
            kasa.info(`THERE IS AN ERROR GETTING INVOICE : ${response['message']}`)
        } else {
            kasa.error("FUNCTION ERROR")
        }
    }


    getCustomer(code){
        let payload = {
            "module":"just_costomer",
            "data":{
                "code":code
            }
        }

        return api.call('VIEW',payload,'/cmms/api/')
    }

    viewCustomerAssets(cust_code){
        let response = cmms_cust.getServiceCustomerAssets(cust_code)
        let status,message,customer,assets

        status = response['status_code'];
        message = response['message'];
        kasa.info("LOADING DATA......")
        setTimeout(
            function () {
                if (status === 200){

                    customer = message['customer'];
                    assets = message['assets'];

                    let count = assets.length
                    let tr = ''
                    if (count > 0){
                        for (let a = 0; a < count; a++) {
                            let asset = assets[a];
                            let code = asset['code'];

                            let service_payload = {
                                "module":"service_history",
                                "data":{
                                    "asset":code
                                }
                            }

                            let service_request = api.call('VIEW',service_payload,'/cmms/api/')
                            let last_services = "NONE"
                            if (service_request['status_code'] === 200){
                                // get counts
                                let serv_tr = ''
                                let s_message = service_request['message'];
                                if (s_message.length > 0){
                                    let target = s_message[0]
                                    last_services = target['date']
                                }
                            }

                            tr += `
                                <tr>
                                    <td>${asset['name']}</td><td>${asset['number']}</td><td>${asset['model']}</td><td>${asset['chassis']}</td>
                                    <td><i onclick="cmms_cust.viewAssetServiceHistory('${code}','${cust_code}')" class="text-info pointer">${last_services}</i></td>
                                    <td><i class="pointer text-info bi-chat-text" onclick="cmms.viewFollowups('${asset['number']}')"></i></td>
                                </tr>
                            `
                        }

                        let html = `
                            <table class="table table-bordered table-sm datatable">
                                <thead><tr><th>NAME</th><th>NUMBER</th><th>MODEL</th><th>CHASSIS</th><td>LAST SERVICED</td><td>FOLLOWS</td></tr></thead>
                                <tbody id="custAsset">${tr}</tbody>
                            </table>
                        `
                        //cust_code
                        let customer_load = {
                            "module":"customer",
                            "data":{
                                "cust_type":"cmms_service",
                                'cust_code':cust_code
                            }
                        }

                        let cus_resp = api.call('VIEW',customer_load,'/cmms/api/');
                        console.table(cus_resp)
                        if(cus_resp['status_code'] === 200){
                            let cust = cus_resp['message'][0]['name']
                            $('#g_modal_title').text(`${cust} SERVICE HISTORY`)
                        } else {
                            $('#g_modal_title').text('CUSTOMER SERVICE HISTORY')
                        }

                        $('#g_modal_size').removeClass(' modal-dialog-centered')
                        $('#g_modal_size').addClass('modal-xl')
                        $('#g_modal_body').html(html)
                        $('#g_modal').modal('show')

                    } else {
                        kasa.warning("There are no assets for customer")
                    }

                } else {
                    // console.table(response)
                    kasa.error(`There is an error getting assets : ${message}`);
                }
            },3000
        );



    }

    viewAssetServiceHistory(code,cust_code){
        let service_payload = {
            "module":"service_history",
            "data":{
                "asset":code
            }
        }

        let response = api.call('VIEW',service_payload,'/cmms/api/')

        if(response['status_code'] === 200){
            let tr = ''
            let message = response['message']
            console.table(message)
            for (let s = 0; s < message.length; s++) {
                let invoice = message[s]

                let invoice_no,date,tot_amt,tax_amt,net_amt,lab_amt,mat_amt
                tr += `<tr>
                            <td><i onclick="cmms_cust.invoicePreview('${invoice['invoice']}','')" class="pointer text-info">${invoice['invoice']}</i></td>
                            <td>${invoice['date']}</td>
                            <td>${invoice['tot_amt']}</td>
                            <td>${invoice['tax_amt']}</td>
                            <td>${invoice['net_amt']}</td>
                       </tr>`
                let trans = invoice['trans']
            }

            let tab = `
                <button onclick="cmms_cust.viewCustomerAssets('${cust_code}')" class="btn btn-info">ASSETS</button> <hr>
                <table class="table table-sm">
                    <thead>
                        <tr><th>INVOICE</th><th>DATE</th><th>NET</th><th>TAX</th><th>GROSS</th></th>
                    </thead>
                    <tbody>
                        ${tr}
                    </tbody>
                </table>
            `
            $('#g_modal_title').text("INVOICES")
            $('#g_modal_body').html(tab)


        } else {
            kasa.error(`THERE IS AN ERROR GETTING SERVICE DETAILS : ${response['message']}`)
        }

    }

    triggerFollowUp(car_no){
        $('#car_no').val(car_no)
        $('#newFolloup').modal('show')
    }

}

class CmmsSales{
    getCustomer(key='all'){
        let payload = {
            module:'cmms_sales_customer',
            data:{
                'key':key
            }
        }

        return api.call('VIEW',payload,'/cmms/api/')
    }

    viewTransactions(deal) {
        amodal.setTitleText("CUSTOMER TRANSACTIONS")
        amodal.setSize('XL')

        let payload = {
            'module': 'cmms_sales_deal',
            data: {
                'deal': deal
            }
        }

        let response = api.call('VIEW', payload, '/cmms/api/');
        let in_deal, trans;

        if (response['status_code'] === 200) {
            let message = response['message']
            in_deal = message['deal']
            trans = message['trans']

            let status = in_deal['status']
            let close = `<button disabled class="btn btn-light">DEAL CLOSED</button>`,new_tran = close;


            if(status === 0){
                close = `<button onclick="cmms_sales.closeDeal(${in_deal['pk']})" class="btn btn-warning">CLOSE DEAL</button>`;
                new_tran = `<button onclick="cmms_sales.newDealTransaction('${deal}')" class="btn btn-info">NEW TRANSACTION</button>`;
            }


            // render page
            let html = `<div class="container-fluid p-2">
                        <div class="row d-flex flex-wrap">
                            <div class="col-sm-4">
                                <div class="card">
                                    <div class="card-header"><strong class="card-title">ASSET DETAILS</strong></div>
                                    <div class="card-body p-2">
                                        <table class="table m-0 table-sm table-bordered">
                                            <tr><td><strong>ASSET</strong></td><td>${in_deal['asset']['name']}</td></tr>
                                            <tr><td><strong>STOCK TYPE</strong></td><td>${in_deal['asset']['stock_type']}</td></tr>
                                            <tr><td><strong>MODEL</strong></td><td>${in_deal['asset']['model']}</td></tr>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            <div class="col-sm-8">
                                <div class="card">
                                    <div class="card-header">
                                        <div class="w-100 d-flex flex-wrap">
                                            <div class="w-50"><strong class="card-title">REQUIREMENT</strong></div>
                                            <div class="w-50 d-flex flex-wrap justify-content-end">${close}</div>
                                        </div>
                                    </div>
                                    <div class="card-body p-2">
                                        <p class="card-text">${in_deal['asset']['requirement']}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <hr>
                        <div class="card">
                            <div class="card-header clearfix">${new_tran}</div>
                            <div class="card-body overflow-auto p-2" style="height: 30vh" id="saleTransactions">
                                <div class="w-100 h-100 d-flex flex-wrap align-content-center justify-content-center"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div></div>
                            </div>
                        </div>
                        
            
                    </div>`
            amodal.setBodyHtml(html)
            amodal.show()

            // make transactions

            let tran_tr = ''
            for (let tr = 0; tr < trans.length; tr++) {
                let tran = trans[tr]
                tran_tr += `<tr><td>${tran['owner']['username']}</td><td>${tran['title']}</td><td>${tran['timestamp']['d_created']} ${tran['timestamp']['t_created']}</td><th><i onclick="alert('${tran['details']}')" class="bi bi-info-circle text-info pointer"></i></th></tr>`
            }
            let neg_html = `<div class="w-100 h-100 d-flex flex-wrap align-content-center justify-content-center"><div class="alert alert-warning">NO TRANSACTION</div></div>`

            if(trans.length > 0 ){
                neg_html = `
                    <table class="table table-sm table-bordered datatable">
                        <thead><tr><th>SALES REP</th><th>TITLE</th><th>DATE</th><th>ACTION</th></tr></thead>
                        <tbody>
                            ${tran_tr}
                        </tbody>
                    </table>
                `
            }

            setTimeout(function () {
                $('#saleTransactions').html(neg_html)
            }, 3)

            } else if (response['status_code'] === undefined) {
                kasa.warning(`UNKNOWN ERROR : PAYLOAD ${JSON.stringify(payload)}`)
            } else {
                kasa.warning(response['message'])
            }



    }
    getDeals(customer){
        let payload = {
            'module':'cmms_sales_deals',
            'data':{
                'sales_customer':customer
            }
        }

        return api.call('VIEW',payload,'/cmms/api/')

    }

    viewDeals(customer){
        let deals = cmms_sales.getDeals(customer)
        if(deals['status_code'] === 200){
            let message = deals['message']
            let tr = ''
            for (let d = 0; d < message.length; d++) {
                let asset,buyer,seller, deal = message[d]
                asset = deal['asset']
                buyer = deal['purch_rep']
                seller = deal['sales_rep']
                let st = ''
                if(deal['status'] === 0){
                    st = `<kbd class="bg-warning">OPEN</kbd>`
                } else if(deal['status'] === 1){
                    st = `<kbd class="bg-success">CLOSED</kbd>`
                } else {
                    st =`<kbd class="bg-light">UNKNOWN STATE</kbd>`
                }

                tr += `
                    <tr>
                        <th>${seller['username']}</th>
                        <td><i class="bi bi-building"></i> ${buyer['company']} <br> <i class="bi bi-person"></i> ${buyer['name']}</td>
                        <td><i class="bi bi-car-front"></i> ${asset['name']} <br> <i class="bi bi-calendar"></i> ${asset['model']}</td>
                        <td><i class="bi bi-phone"></i> ${buyer['phone']} <br> <i class="bi bi-mailbox"></i> ${buyer['email']}</td>
                        <td>${deal['date']} ${deal['time']}</td>
                        <td>${st}</td>
                        <td><i title="transactions" onclick="cmms_sales.viewTransactions('${deal['pk']}')" class="bi text-info pointer bi-view-list"></i></td>
                    </tr>
                `

            }
            $('#tbody').html(tr)

        } else {
            kasa.info(`${deals['message']}`)
        }
    }

    saveDeal(){

        // validate values
        let ok = anton.validateInputs(['sales_rep','sales_customer','pur_rep_name','pur_rep_email','pur_rep_phone','asset','model','stock_type','requirement'])
        if(ok){
            let customer = $('#sales_customer').val()
            let payload = {
                "module":"sales_deal",
                "data":{
                    "sales_rep":$('#sales_rep').val(),
                    "sales_customer":customer,
                    "pur_rep_name":$('#pur_rep_name').val(),
                    "pur_rep_email":$('#pur_rep_email').val(),
                    "pur_rep_phone":$('#pur_rep_phone').val(),
                    "asset":$('#asset').val(),
                    "model":$('#model').val(),
                    "stock_type":$('#stock_type').val(),
                    "requirement":$('#requirement').val()
                }
            }

            let request = api.call('PUT',payload,'/cmms/api/')
            $('#newDeal').modal('hide')
            kasa.info(request['message'])
            cmms_sales.viewDeals(customer)

        } else {
            kasa.info("FILL ALL FIELDS")
        }

    }

    newDealTransaction(deal){
        amodal.hide()
        Swal.fire({
            title: 'ADD TRANSACTION',
            html: `<input placeholder="Title" id="tran_title" class="form-control form-control-sm rounded-0 mb-2"> <textarea id="tran_detail" class="form-control form-control-sm" rows="5"></textarea>`,
            showCancelButton: true,
            confirmButtonText: 'SAVE',
            cancelButtonText: 'Cancel',
            reverseButtons: true, // To swap the positions of "Cancel" and "OK" buttons
          }).then((result) => {
            // Check if the user clicked "OK"
            if (result.isConfirmed) {
                if(anton.validateInputs(['tran_title','tran_detail','mypk']))
                {
                    let title = $('#tran_title').val(),detail=$('#tran_detail').val()
                    let payload = {
                        'module':'deal_transaction',
                        data:{
                            'deal':deal,
                            'title':title,
                            'detail':detail,
                            'owner':$('#mypk').val()
                        }
                    }
                    let response = api.call('PUT',payload,'/cmms/api/')

                    if(response['status_code'] !== 200){
                        kasa.warning(response['message'])
                    } else if(response['status_code'] === undefined){
                        kasa.error("THERE IS A SYSTEM ERROR")
                    }
                    // kasa.info(title)
                    cmms_sales.viewTransactions(deal)

                } else {
                    kasa.info("FILL ALL FIELDS")
                    setTimeout(function () {
                        cmms_sales.newDealTransaction(deal)
                    },3000);
                }

            } else {
              cmms_sales.viewTransactions(deal)
            }
          });
    }

    // delete customer
    delete_customer(key){
        let payload = {
            'module':'sales_customer',
            data:{
                'key':key
            }
        }

        let response = api.call('DELETE',payload,'/cmms/api/')
        kasa.set_message(response['message'])
        window.reload()
    }


    closeDeal(deal) {
        amodal.hide()

        Swal.fire({
            title: 'CLOSING REMARK',
            html:
                '<select id="swal-select" class="form-control mb-2">' +
                '<option selected value="0">FAILED</option>' +
                '<option value="1">SUCCES</option>' +
                '</select>' +
                `<textarea id="swal-textarea" class="form-control" placeholder="Type your message here..."></textarea>`,
            showCancelButton: true,
            confirmButtonText: 'Submit',
            cancelButtonText: 'Cancel',
            allowEscapeKey: false,
            allowOutsideClick: false,
            preConfirm: function() {
                return [
                    document.getElementById('swal-select').value,
                    document.getElementById('swal-textarea').value
                ];
            }
        }).then((result) => {
            if (result.isConfirmed) {
                console.log('Selected option: ', result.value[0]);
                console.log('Text area value: ', result.value[1]);
                let close_payload = {
                    module:'close',
                    data:{
                        'doc':'deal',
                        'key':deal,
                        message: result.value[1],
                        closer:$('#mypk').val(),
                        finale: result.value[0]
                    }
                };

                let request = api.call('PATCH', close_payload, '/cmms/api/')
                kasa.confirm(request['message'],1,'here')

            } else if (result.dismiss === Swal.DismissReason.cancel) {
                amodal.show()
            }
        });
    }
}

const cmms_cust = new CmmsCust()
const cmms_sales = new CmmsSales()