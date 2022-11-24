class Grn {
    SaveNew(){

        // validate
        let loc,loc_to,remarks,er_msg,er_count,rows

        loc = $('#loc').val()
        remarks = $('#remarks').val()

        // alert(loc_fr)

        er_count = 0;
        er_msg = ''

        if(loc.length < 1)
        {
            er_count ++
            er_msg += `<p>Select Location</p>`
        }

        if(remarks.length < 1)
        {
            er_count ++
            er_msg += `<p>Remarks cannot be empty</p>`
        }

        // alert(er_count)

        if(er_count < 1)
        {

            // validate rows
            rows = $('#tBody tr').length
            if(rows > 0)
            {
                let tran_err_count = 0;
                let tran_err_msg = ''

                for (let i = 0; i < rows; i++) {

                    let qty,total

                    // get row ids
                    let qty_id = `#qty_${i}`
                    let row_id = `#row_${i}`
                    let total_id = `#total_${i}`

                    qty = $(qty_id).val()
                    total = $(total_id).val()

                    if(total == 0)
                    {
                        // append quantity error
                        tran_err_count ++
                        tran_err_msg += `<p>line number ${row_id}  : Cannot Make a transfer of 0</p>`
                    }


                }
                if(tran_err_count > 0)
                {
                    swal_response('error',"VALIDATION FAILED",tran_err_msg)
                } else
                {
                    // transact
                    let hd = JSON.parse(api_call('grn', 'new_hd', {'loc':loc,'remark':remarks}))

                    if(hd['status'] === 200)
                    {
                        // proceed
                        let ret_hd = hd['message']
                        for (let xi = 0; xi < rows; xi++)
                        {
                            //insert each line
                            let qty_id,row_id,total_id,qty,total,barcode_id,pack_id,barcode,pack
                            qty_id = `#qty_${xi}`
                            row_id = `#row_${xi}`
                            total_id = `#total_${xi}`
                            barcode_id = `#barcode_${xi}`
                            pack_id = `#pack_${xi}`


                            barcode = $(barcode_id).val()

                            qty = $(qty_id).val()
                            total = $(total_id).val()
                            pack = $(pack_id).val()

                            let data = {'parent':ret_hd,"line":xi,"product":barcode,"packing":pack,"quantity":qty,"total":total}

                            api_call('transfer','new_tran',data)

                        }

                        location.href='/admin_panel/inventory/transfer/'


                    } else
                    {
                        swal_response('error',"",`could not create transfer header ${hd['message']}`)
                    }

                }


            } else
            {
                swal_response('error','VALIDATION','Cannot save an empty transaction')
            }

        }
        else
        {
            // alert('there is an error')
            swal_response('error','VALIDATION FAILED',er_msg)
        }


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
            cost = response['cost']
            trans = response['trans']

            // load header
            $('#type').val("PO")
            $('#ref').val(header['entry_no'])

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


                    // get packing
                    packing_option = ''


                    row += `<tr id="row_${sn}">
                                <td>${sn} <input type="hidden" id="pack_${sn}" value=""> </td>
                                <td id="barcode_${sn}">${barcode}</td>
                                <td id="descr_${sn}">${descr}</td>
                                <td><select onchange="productMaster.TranPack(this.value,${sn});productMaster.TranRowCalc('${sn}')" name="" id="packing_${sn}" class="anton-form-tool form-control-sm">${packing_option}</select></td>
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

}

const grn = new Grn()