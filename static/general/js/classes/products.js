class Products {

    GetProduct(barcode)
    {
        var result = 0;
        let form_data;
        form_data = {
            'for':'get_product',
            'query':barcode
        }

        $.ajax({
            url:$('#search_url').val(),
            data:form_data,
            'async': false,
            'type': "GET",
            'global': false,
            'dataType': 'html',
            success: function (response){
                result = response;
            }
        })

        return result;

    }

    GetProductPacking(barcode)
    {
        let form_data;
        form_data = {
            'for':'get_prod_packing',
            'query':barcode
        }

        var result = 0

        $.ajax({
            url:$('#search_url').val(),
            data:form_data,
            'async': false,
            'type': "GET",
            'global': false,
            'dataType': 'html',
            success: function (response){
                result = response
            }
        })

        return result

    }

    Stock(pk)
    {

        let stock = JSON.parse(api_call('products','get_stock',{'pk':pk}))

        console.table(stock['message'])

        let tr = ''

        for (let i = 0; i < stock['message'].length; i++) {
            let row = stock['message'][i]

            tr += `<tr><td>${row['loc']}</td><td>${row['loc_descr']}</td><td>${row['stock']}</td></tr>`

        }

        let thd = `<table class="table table-sm table-info"><thead><tr><th>CODE</th><th>LOCATION</th><th>STOCK</th></tr></thead>`
        let tbd = `<tbody>${tr}</tbody></table>`
        $('#g_modal_title').text('STOCK REPORT')
        $('#g_modal_body').html(thd + tbd)
        $('#g_modal').modal('show')

    }

    // fill item document transaction
    FillTranList(barcode){
        let product_request = apiv2('product','get_product',{'barcode':barcode})
        let product_response = JSON.parse(product_request)
        if(product_response['status'] === 200)
        {
            // there is a positive result
            let product = JSON.parse(JSON.stringify(product_response['message']))
            // console.table(product)
            let group,others,prod_details,prod_pack,supplier,tax

            others = product['others']

            let barcode,descr
            prod_details = product['prod_details']
            barcode = prod_details['barcode']
            descr = prod_details['prod_sht_descr']

            prod_pack = product['prod_pack']
            let packing_option = ''
            let pack_descr = ''
            let gen_pack_qty = ''
            for (let i = 0; i < prod_pack.length; i++) {
                let packing = prod_pack[i]
                let pack_code,pack_type,pack_qty,opt = "UNKNOWN"
                pack_code = packing['pack_code']
                pack_type = packing['pack_type']
                let ppk = packing['pk']
                pack_qty = packing['pack_qty']

                let sel = ''

                if(pack_type === 'A')
                {
                    opt = "ISSUE"

                } else if(pack_type === 'P')
                {
                    opt = "PURCHASING"
                    sel = "selected"
                    pack_descr = packing['pack_descr']
                    gen_pack_qty = pack_qty
                }

                packing_option += `<option ${sel} value="${ppk}"> ${pack_type} - ${packing['pack_code']}</option>`

            }
            // console.log(pack_descr)

            let sn = $('#tBody tr').length + 1

            let row = `<tr id="row_${sn}">
                                <td>${sn} <input type="hidden" id="pack_${sn}" value=""> </td>
                                <td id="barcode_${sn}">${barcode}</td>
                                <td id="descr_${sn}">${descr}</td>
                                <td><select onchange="productMaster.TranPack(this.value,${sn});productMaster.TranRowCalc('${sn}')" name="" id="packing_${sn}" class="anton-form-tool form-control-sm">${packing_option}</select></td>
                                <td><input type="number" readonly style="width: 50px" value="${gen_pack_qty}" id="pack_qty_${sn}"></td>
                                <td><input type="number" onchange="productMaster.TranRowCalc('${sn}')" style="width: 100px" class="anton-form-tool form-control-sm" id="tran_qty_${sn}" value="1"></td>
                                
                                <td><input type="number" onchange="productMaster.TranRowCalc('${sn}')" style="width: 100px"  class="anton-form-tool form-control-sm" id="un_cost_${sn}" value="${others['cost_price']}"></td>
                                <td><input readonly type="number" style="width: 100px"  class="anton-form-tool form-control-sm" id="tot_cost_${sn}" value="${others['cost_price']}"></td>
                            </tr>`

            // confirm it item exist in transaction
            let item_exit = 0
            for (let i = 1; i <= sn; i++) {
                let barcode_row = `barcode_${i}`
                let bbarcode = $(`#${barcode_row}`)
                let bb_val = bbarcode.text()
                // console.log(`row barcode : ${bb_val}`)
                if(bb_val === barcode)
                {
                    item_exit += 1
                }
            }

            if(item_exit < 1){
               $('#tBody').append(row)
            }




        } else {
            // no response
            console.log(product_response['message'])

        }
    }

    // calculate item trans
    TranRowCalc(id)
    {
        let row_id,barcode_id,descr_id,packing_id,tan_qty_id,total_qty_id,
            un_cost_id,tot_cost_id

        row_id = $(`#row_${id}`)
        packing_id = $(`#pack_qty_${id}`)
        tan_qty_id = $(`#tran_qty_${id}`)
        total_qty_id = $(`#total_qty_${id}`)
        un_cost_id = $(`#un_cost_${id}`)
        tot_cost_id = $(`#tot_cost_${id}`)

        let pack_qty,tran_qty,tran_math,un_cost,tot

        pack_qty = packing_id.val()
        tran_qty = tan_qty_id.val()

        tran_math = pack_qty * tran_qty

        un_cost = un_cost_id.val()
        tot = un_cost * tran_math

        tot_cost_id.val(tot)
        console.log(tot)




    }


    TranPack(pack_pk,line_no) {
        let data = {
            'pk':pack_pk
        }

        let api_req,status,message
        api_req = JSON.parse(apiv2('general','prodPack',data))

        status = api_req['status']
        message = api_req['message']

        if(status === 200)
        {
            let pack_qty = message['pack_qty']
            $(`#pack_qty_${line_no}`).val(pack_qty)

        }
    }

    ApprTrans(doc,entry)
    {
        let api_rsp,status,message
        api_rsp = apiv2('doc_approve','approve',{'doc':doc,'entry':entry,'user':$('#mypk').val()})
        status = api_rsp['status']
        message = api_rsp['message']

        swal_response('info',status,message)
    }

    loadProdMastScreen(barcode){
        let fetch = api.view({'module':'product','data':{'barcode':barcode}})
        if(fetch['status_code'] === 200){
            let response = fetch['message']
            let count = response['count']
            if(count === 1){
                let group = response['group']
                let product = response['product']
                let stock = response['stock']
                let tax = response['tax']
                let supplier = response['supplier']
                let cardex = response['cardex']
                let nav = response['nav']

                // nav
                if(nav['next'] === 'Y'){
                    // enable next
                    $('#next_nav').prop('disabled',false)
                    $('#next_nav').val(nav['next_prod'])
                } else
                {
                    // disable next
                    $('#next_nav').prop('disabled',true)
                }

                if(nav['prev'] === 'Y'){
                    // enable next
                    $('#prev_nav').prop('disabled',false)
                    $('#prev_nav').val(nav['prev_prod'])
                } else
                {
                    // disable next
                    $('#prev_nav').prop('disabled',true)
                }


                // load group
                $('#group').val(group['group'])
                $('#sub_group').val(group['sub_grp'])

                // load produc details
                $('#barcode').val(product['barcode'])
                $('#description').val(product['descr'])

                // packing
                $('#pack_unit').val()
                $('#pack_qty').val()

                //image
                $('#prd_img').prop('src',product['image'])

                //tax
                $('#tax_group').val(tax['tax_code'])
                $('#last_cost_price').val(supplier['last_rec_price'])

                // stock
                let stktr = ''
                for (let s = 0; s < stock['trans'].length ; s++) {
                    let st = stock['trans'][s]
                    stktr += `<tr><td>${st['loc_id']}</td><td>${st['loc_desc']}</td><td>${st['stock']}</td></tr>`
                }
                $('#stock_table').html(stktr)

                // cardex
                let cadtr = ''
                for (let c = 0; c < cardex.length ; c++) {
                    let cad = cardex[c]
                    cadtr += `<tr><td>${cad['date']}</td><td>${cad['doc_type']}</td><td>${cad['entry_no']}</td><td>${cad['loc_id']}</td><td>${cad['loc_desc']}</td><td>${cad['qty']}</td></tr>`
                }
                $('#cardex_table').html(cadtr)

            }



            ctable(response)
        }

    }

}

const productMaster = new Products()