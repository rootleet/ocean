

class Grn {
    SaveNew(){

        swal_success('SAVING GRN TRANSACTION')
        /*
        * VALIDATE GRN ENTRIES
        * MAKE SURE SUPPLIER IS SELECTED AND EXIST
        * VALIDATE LOCATION
        * VALID TYPE AND REFERENCE
        * VALIDATE TAX COMPONENT
        * VALIDATE REMARKS*/

        let tran_list = $('#tbody tr').length
        let supplier,loc,type,ref,taxable_amt,tax_amt,tot_amt,remark,err_count,err_msg
        supplier = $('#supplier').val()
        loc = $('#loc').val()
        type = $('#type').val()
        ref = $('#ref').val()
        taxable_amt = $('#invoice_amt').val()
        tax_amt = $('#tax_amt').val()
        tot_amt = $('#tot_amt').val()
        remark = $('#remark').val()
        err_msg = ""
        err_count = 0

        if(
            supplier.length < 1 ||
            loc.length < 1 ||
            type.length < 1 ||
            ref.length < 1 ||
            taxable_amt.length < 1 ||
            tax_amt.length < 1 ||
            tot_amt.length < 1 ||
            remark.length < 1
        ){
            err_count ++
            err_msg = "Invalid HEater"
        }

        var fileInput = $('#image-input')[0];
        var file = fileInput.files[0];

        if(file){

        } else {
            err_count ++
            err_msg += ` Please select a file`
        }

        if(err_count > 0)
        {
            swal_response('','',err_msg)
        } else  {

            if(tran_list > 0)
            {
                let tran_err_count = 0
                let tran_err_msg = 'error%% '
                for (let i = 1; i <= tran_list ; i++) {

                        let row,barcode,descr,packing,pack_descr,tran_qty,un_cost,tot_cost
                        row = $(`#row_${i}`)
                        barcode = $(`#barcode_${i}`)
                        descr = $(`#descr_${i}`)
                        packing = $(`#packing_${i}`)
                        pack_descr = $(`#pack_descr_${i}`)
                        tran_qty = $(`#tran_qty_${i}`)
                        un_cost = $(`#un_cost_${i}`)
                        tot_cost = $(`#tot_cost_${i}`)

                        if(tran_qty.val() <= 0){
                        tran_err_count ++
                        tran_err_msg += `<p>Line ${i} quantity is invalid</p>`
                        }
                        if(un_cost.val() <= 0){
                            tran_err_count ++
                            tran_err_msg += `<p>Line ${i} unit cost is invalid</p>`
                        }
                        if(tot_cost.val() <= 0){
                            tran_err_count ++
                            tran_err_msg += `<p>Line ${i} total cost is invalid</p>`
                        }

                }

                if(tran_err_count <= 0){
                    let data = {
                'supplier':supplier,
                'location':loc,
                'type':type,
                'taxable_amt':taxable_amt,
                'tax_amt':tax_amt,
                'tot_amt':tot_amt,
                'remark':remark,
                'taxable':$('#taxable').val(),
                'owner':$('#mypk').val(),
                'ref':$('#ref').val()
            }
                    console.table(data)

                    let status,message,grnhd = JSON.parse(apiv2('grn','newHd',data))
                    status = grnhd['status']
                    message = grnhd['message']
                    console.table(grnhd)
                    if(status === 200)
                    {
                        
                        let entry_no = message
                        for (let i = 1; i <= tran_list ; i++) {

                            let row, barcode, descr, packing, pack_descr, tran_qty, un_cost, tot_cost,pack_qty
                            row = $(`#row_${i}`)
                            barcode = $(`#barcode_${i}`)
                            descr = $(`#descr_${i}`)
                            packing = $(`#packing_${i}`)
                            pack_descr = $(`#pack_descr_${i}`)
                            tran_qty = $(`#tran_qty_${i}`)
                            un_cost = $(`#un_cost_${i}`)
                            tot_cost = $(`#tot_cost_${i}`)
                            pack_qty = $(`#pack_qty_${i}`)

                            let data = {
                                "entry_no":entry_no,
                                "line":i,
                                "barcode":barcode.text(),
                                "packing":packing.val(),
                                'pack_qty':pack_qty.val(),
                                "qty":tran_qty.val(),
                                "total_qty":packing.val() *  tran_qty.val() ,
                                "un_cost":un_cost.val(),
                                "tot_cost":tot_cost.val()
                            }

                            let exe = apiv2('grn','newTran',data)
                            console.table(data)
                            console.table(JSON.parse(exe))


                        }
                        // close po
                        if(type === 'PO')
                        {
                            apiv2('close_doc','null',{'entry':ref,'user':$('#mypk').val(),'doc':'po'})
                        }


                        // uplaod file



                        // Create a FormData object to store the file data
                        var formData = new FormData();
                        formData.append('file', file);
                        formData.append('entry_no',entry_no)
                        formData.append('doc','GR')

                        // Send the file data to the server using AJAX
                        $.ajax({
                          url: '/doc_upload/',  // Replace with the actual server endpoint for uploading
                          type: 'POST',
                          data: formData,
                          processData: false,
                          contentType: false,
                          success: function(response) {
                            // Handle the server response after successful upload
                            console.log('Upload successful');
                            // Additional code here
                          },
                          error: function(xhr, status, error) {
                            // Handle the error response
                            console.error('Upload error: ' + error);
                            // Additional code here
                          }
                        });



                        location.href = '/inventory/grn/'

                    } else {
                        error_handler(`error%%${message}`)
                    }

                }






            } else {
                error_handler(`error%%Cannot save empty document`)
            }

        }



        // start validations
        // let supp_req = apiv2('')

    }

    retrievePo(po_number){
        let po_req = apiv2('po','get',{"entry":po_number})
        let po_response = JSON.parse(po_req)

        if(po_response['status'] === 200)
        {
            // there is response
            let response = po_response['message']
            let header,cost,trans
            header = response['header']
            console.table(header)
            cost = response['cost']
            trans = response['trans']

            // load header
            $('#type').val("PO")
            $('#ref').val(header['entry_no'])
            $('#invoice_amt').val(cost['taxable_amt'] - cost['tax_amt'])
            $('#tot_amt').val(cost['taxable_amt'])
            $('#tax_amt').val(cost['tax_amt'])

            let  tax_htm= ''
            if(cost['taxable'] === 1)
            {
                tax_htm= `<option value="1" selected>YES</option><option value="0">NO</option>`
            } else {
                tax_htm = `<option value="1" >YES</option><option selected value="0">NO</option>`
            }
            $('#taxable').html(tax_htm)

            // get suppliers
            let sup_req,sup_resp,supp_stat,supp_msg
            sup_req = apiv2('general','getSuppliers','none')
            sup_resp = JSON.parse(sup_req)
            supp_stat = sup_resp['status']
            supp_msg = sup_resp['message']
            let sopt = ''
            if(supp_stat === 200)
            {
                // there is suppler
                for (let i = 0; i < supp_msg.length; i++) {
                    let s = supp_msg[i]
                    console.table(s)
                    let company = s['company']

                    let pk = s['pk']

                    if(header['supp_pk'] === pk)
                    {
                        sopt += `<option selected value="${pk}" >${company}</option>`
                    } else
                    {
                        sopt += `<option value="${pk}" >${company}</option>`
                    }
                }
            }
            $('#supplier').html(sopt)

            // location
            let loc_req,loc_res,loc_stat,loc_msg,loc_row = ''
            loc_req = apiv2('general','getLocs','nonw')
            loc_res = JSON.parse(loc_req)
            loc_stat = loc_res['status']
            loc_msg = loc_res['message']

            if(loc_stat === 200)
            {
                // there is suppler
                for (let i = 0; i < loc_msg.length; i++) {
                    let s = loc_msg[i]
                    console.table(s)
                    let loc_code = s['code']
                    let pk = s['pk']
                    let descr = s['descr']

                    if(header['loc_code'] === descr)
                    {
                        loc_row += `<option selected value="${pk}" >${loc_code} - ${descr}</option>`
                    } else
                    {
                        loc_row += `<option value="${pk}" >${loc_code} - ${descr}</option>`
                    }
                }
            }

            $('#loc').html(loc_row)
            $('#remark').val(header['remark'])

            // fill trans FillTranList
            let tran_count, tran_list
            tran_count = trans['count']
            tran_list = trans['transactions']
            if(tran_count > 0)
            {
                // load grn trans from po
                console.log("TRAN LIST")
                console.table(tran_list)
                let row = ''
                for (let i = 0; i < tran_list.length; i++)
                {
                    let tran = tran_list[i]
                    let line,packing,barcode,descr,qty,tot_cost,un_cost,pack_code,pack_qty,packing_option,pack_pk
                    line = tran['line']

                    packing = tran['packing']
                    pack_pk = packing['pk']
                    pack_code = packing['pack_code']
                    pack_qty = packing['pack_qty']

                    barcode = tran['product_barcode']
                    descr = tran['product_descr']
                    qty = tran['qty']
                    tot_cost = tran['tot_cost']
                    un_cost = tran['un_cost']
                    let sn = line

                    // get product details
                    let product = JSON.parse(apiv2('product','get_product',{'barcode':barcode}))['message']
                    let prod_pack = product['prod_pack']
                    let packoptions = ''

                    console.table(product)

                    for (let j = 0; j < prod_pack.length; j++) {
                        let p_pack = prod_pack[j]
                        let p_pk = p_pack['pk']
                        let p_code = p_pack['pack_code']
                        let p_type = p_pack['pack_type']


                        if (p_pk === pack_pk)
                        {
                            packoptions += `<option selected value="${p_pk}">${p_type} - ${p_code}</option>`
                        } else
                        {
                            packoptions += `<option value="${p_pk}">${p_type} - ${p_code}</option>`
                        }

                    }

                    console.log('product details')
                    console.table(prod_pack)
                    console.log('product details')


                    // get packing
                    packing_option = ''


                    row += `<tr id="row_${sn}">
                                <td>${sn} <input type="hidden" id="pack_${sn}" value=""> </td>
                                <td id="barcode_${sn}">${barcode}</td>
                                <td id="descr_${sn}">${descr}</td>
                                <td><select onchange="productMaster.TranPack(this.value,${sn});productMaster.TranRowCalc('${sn}')" name="" id="packing_${sn}" class="anton-form-tool form-control-sm">${packoptions}</select></td>
                                <td><input type="number" readonly style="width: 50px" value="${pack_qty}" id="pack_qty_${sn}"></td>
                                <td><input type="number" onchange="productMaster.TranRowCalc('${sn}')" style="width: 100px" class="anton-form-tool form-control-sm" id="tran_qty_${sn}" value="${qty}"></td>
                                
                                <td><input type="number" onchange="productMaster.TranRowCalc('${sn}')" style="width: 100px"  class="anton-form-tool form-control-sm" id="un_cost_${sn}" value="${un_cost}"></td>
                                <td><input readonly type="number" style="width: 100px"  class="anton-form-tool form-control-sm" id="tot_cost_${sn}" value="${tot_cost}"></td>
                            </tr>`

                }

                $('#tbody').html(row)

            } else
            {
                swal_response('THERE IS NO FISH')
            }






            // console.table(response)
            $('#po').modal('hide')
        } else
        {
            // wrong response

        }
    }

    loadGrn(entry_no){
        let hd_req = apiv2('grn','get',{"entry":entry_no})
        let hd_res = JSON.parse(hd_req)

        if(hd_res['status'] === 200)
        {

            let message = hd_res['message']

            let header,trans
            header = message['header']
            trans = message['trans']

            $('#loc').val(`${header['loc_code']} - ${header['loc_descr']}`)
            $('#supplier').val(header['supp_descr'])
            $('#ent_date').val(header['entry_date'])
            $('#ent_num').val(header['entry_no'])
            $('#ent_rm').val(header['remark'])
            $('#t_owner').val(header['owner'])
            $('#print').val(header['pk'])
            $('#approve').val(header['pk'])
            console.table(trans)
            if(trans['count'] > 0)
            {
                // make trans row
                let transactions = trans['transactions']
                let row = ''
                for (let i = 0; i < transactions.length; i++) {
                    let tran = transactions[i]
                    let packing = tran['packing']
                    console.table(packing)

                    row += `<tr>
                                <td>${tran['line']}</td>
                                <td>${tran['product_barcode']}</td>
                                <td>${tran['product_descr']}</td>
                                <td>${packing['code']}</td>
                                <td>${packing['pack_qty']}</td>
                                <td>${tran['qty']}</td>
                                <td>${tran['un_cost']}</td>
                                <td>${tran['tot_cost']}</td>
                            </tr>`

                }

                $('#tbody').html(row)
            }

            // navs
            let nav = message['nav']
            let appr = message['appr']
            if(appr['status'] === 0)
            {
                // not approved
                $('#approve').prop('disabled',false)
            } else if(nav['status'] === 1)
            {
                // approved
                $('#approve').prop('disabled',true)

            } else {
                // unknown status
                $('#approve').prop('disabled',true)
            }

            if(nav['next_count'] > 0)
            {
                // there is next
                $('#next').prop('disabled',false)
                $('#next').val(parseInt(nav['next_id']))
            } else {
                // no next
                $('#next').prop('disabled',true)
            }

            if(nav['prev_count'] > 0)
            {
                // there is prev
                $('#prev').prop('disabled',false)
                $('#prev').val(parseInt(nav['prev_id']))
            } else {
                // no prev
                $('#prev').prop('disabled',true)
            }

            // prices
            let prices = message['cost']
            if(prices['taxable'] === 1 )
            {
                $('#taxable').val("YES")
            } else {
                $('#taxable').val("NO")
            }
            $('#taxable_amt').val(prices['taxable_amt'])
            $('#tax_amt').val(prices['tax_amt'])
            $('#tot_amt').val((parseFloat(prices['taxable_amt']) + parseFloat(prices['tax_amt'])).toFixed(2))


        } else
        {
            swal_response('error',"DOCUMENT ERROR",hd_res['message'])
        }
    }

    loadGrDocs(entry_no){

        let data = {
            "module":"doc",
            "data":{
                "entry_no":entry_no,
                "doc":"GR"
            }
        }

        let view = api.view(data)

        if(view['status_code'] === 200){
            let message = view['message']
            let count = message['count']
            let files = message['files']

            let imgss = ''

            if (count < 1){
                imgss = "NO DOCUMENTS"
                $('#g_modal_size').removeClass('modal-lg')
            } else {
                $('#g_modal_size').addClass('modal-lg')
                let imgs = ''
                for (let im = 0; im < files.length ; im++) {
                    let file = files[im]['url']
                    imgss += `<div class="col-sm-3 m-2"><div class="card w-100">
                            <div class="card-body text-center p-2">
                            <img src="${file}" alt="" class="img-fluid img-thumbnail"><br>
                            <button onclick="windowPopUp('${file}','GRN DOCUMENT',900,1000)" class="w-100 btn btn-info rounded-0 mt-1">VIEW</button></div></div></div>`

                }
            }

            let container = `
            <div class="container"><div class="row d-flex flex-wrap justify-content-center">${imgss}</div></div>
            `
            $('#g_modal_title').text("GRN DOCUMENTS")
            $('#g_modal_body').html(container)
            $('#g_modal').modal('show')
            console.log(container)
        }

    }

}

const grn = new Grn()