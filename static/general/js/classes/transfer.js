class Transfer {



    saveTransfer() {

        // validate
        let loc_fr,loc_to,remarks,er_msg,er_count,rows

        loc_fr = $('#loc_fr').val()
        loc_to = $('#loc_to').val()
        remarks = $('#remarks').val()

        // alert(loc_fr)

        er_count = 0;
        er_msg = ''

        if(loc_to == loc_fr)
        {
            er_count ++
            er_msg += `<p>Same location transfer not allowed</p>`
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
                        tran_err_msg += `<p>line number ${row_id}  : Cannot Make a transfer of of 0</p>`
                    }


                }
                if(tran_err_count > 0)
                {
                    swal_response('error',"VALIDATION FAILED",tran_err_msg)
                } else
                {
                    // transact
                    let hd = JSON.parse(api_call('transfer', 'new_hd', {'from':loc_fr,'to':loc_to,'remark':remarks}))
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

    loadScreen(pk){
        var data = {'pk': pk}

        let hd = JSON.parse(api_call('transfer','get_hd',data))
        let tran = JSON.parse(api_call('transfer','get_tran',data))
        let response = hd['message']
        let status = hd['status']


        if(response['status'] === 0)
        {
            // not processed
            $('#adjProcess').val(parseInt(pk))
            $('#adjProcess').prop( "disabled", false );

        } else
        {
            $('#adjProcess').prop( "disabled", true );
        }

        if(response['next_count'] > 0)
        {
            // there is next
            $('#next').val(parseInt(response['next']))
            $('#next').prop( "disabled", false );
        }
        else
        {
            //disable next
            $('#next').prop( "disabled", true );
        }

        if(response['prev_count'] > 0)
        {
            // there is previous

            $('#prev').val(parseInt(response['prev']))
            $('#prev').prop( "disabled", false );
        }
        else
        {
            // disable previous
            $('#prev').prop( "disabled", true );
        }
        $('#loc_fro').val(response['from_code'])
        $('#loc_to').val(response['to'])
        $('#ent_date').val(response['date'])
        $('#ent_num').val(`TR${response['entry_no']}`)
        $('#ent_rm').val(response['remark'])


        let tr =''

        if(tran['status'] == 202)
        {
            for (let i = 0; i < tran['message'].length; i++ ) {
            let t_line = tran['message'][i]
            // console.table(`this is ${t_line['barcode']}`)

            let barcode = t_line['barcode'];

            let descr = t_line['description']
            let pack_qty = t_line['pack_qty']
            let quantity = t_line['quantity']
            let total = t_line['total']

            tr += `<tr>
                                <td>${barcode}</td>
                                <td>${descr}</td>
                                <td>${pack_qty}</td>
                                <td >${quantity}</td>
                                <td>${total}</td>
                            </tr>`
        }
        } else {
            tr =`<tr><td colspan="5"><span class="text-danger">NO DATA</span></td></tr>`
        }



        $('#tbody').html(tr)

    }

    approve(pk) {
        if(confirm('Are you sure you want to approve document?'))
        {
            var data = {'pk': pk}
            // console.table(data)
            let approve = JSON.parse(api_call('transfer','approve',data))
            console.table(approve['message'])



            let stat,msg
            stat = approve['status']
            msg = approve['message']

            if(stat === 505)
            {
                // there is an error in processing transactions
                error_handler(`error%%<strong>${stat}</strong> <p>${msg}</p>`)
            }

            if(stat === 404)
            {
                // no transaction found
                error_handler('error%%Entry Not Found')
            }

            if(stat === 202)
            {
                // document approved
                swal_response('success',stat,msg)
                this.loadScreen(pk)
            }
        }
    }
}

const trans_ini = new Transfer()