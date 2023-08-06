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
}

const cmms_cust = new CmmsCust()
const cmms_sales = new CmmsSales()