class Po {

    // SAVE

    save() {

        // validate
        let loc,supplier,remarks,er_msg,er_count,rows,owner,taxable
        loc = $('#loc').val()
        supplier = $('#supplier').val()
        remarks = $('#remarks').val()
        owner = $('#owner').val()
        taxable = $('#taxable').val()


        er_msg = "error%%"
        er_count = 0

        // validate header
        if(loc === 'none')
        {
            er_msg += "Location Empty | "
            er_count ++
        }

        if(supplier === 'none')
        {
            er_msg += "Select Supplier | "
            er_count ++
        }

        if(remarks.length < 1)
        {
            er_msg += "Empty Remarks "
            er_count ++
        }

        if(er_count > 0)
        {
            error_handler(er_msg)

        } else {
            // check tran list
            let tran_list = $('#tBody tr').length
            if(tran_list > 0)
            {
                let tran_err_count = 0
                let tran_err_msg = 'error%% '
                // loop through each row for error
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

                if(tran_err_count <= 0)
                {
                    let data = {
                        "location":loc,
                        "supplier":supplier,
                        "remarks":remarks,
                        'owner':owner,
                        'taxable':taxable
                    }
                    // create po header
                    let header_req = apiv2('po','newHd',data)
                    let header_resp = JSON.parse(header_req)

                    if(header_resp['status'] === 200)
                    {
                        // get entry number and insert trans
                        let entry_no = header_resp['message']

                        // loop through each row and add to transaction
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

                            apiv2('po','newTran',data)
                            console.table(data)
                            // alert("DATA INSERTED")

                        }

                        location.href = '/inventory/purchasing/'

                    } else {
                        swal_response('info',"",header_resp['message'])
                    }


                } else
                {
                    error_handler(tran_err_msg)
                }


            } else
            {
                swal_response('error','System Error','Cannot save document with empty transactions')
            }
        }




    }

    // SAVE

    // load screen
    loadTrans(entry_no)
    {
        let po_req = apiv2('po','get',{"entry":entry_no})
        let po_res = JSON.parse(po_req)

        if(po_res['status'] === 200)
        {

            let message = po_res['message']

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
            if(nav['status'] === 0)
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
            swal_response('error',"DOCUMENT ERROR",po_res['message'])
        }

    }

    // print
    Print(entry_no){
        console.log(entry_no)
        if(entry_no.length > 0)
        {
            let data = {
            'doc':'po',
            'entry_no':entry_no
        }

            let req = apiv2('general','print',data)
            let res = JSON.parse(req)
            console.table(res)

            if(anton.IsRequest(res))
            {
                windowPopUp(res['file'],'PO PRINT OUT',1024,976)
            } else {
                kasa.response(res)
            }
        } else
        {
            error_handler('error%%Invalid Document Entry Number')
        }
    }

}

const po = new Po()