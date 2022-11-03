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
}

const grn = new Grn()