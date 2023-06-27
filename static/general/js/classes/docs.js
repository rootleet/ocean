class Docs {
    save(doc_type){
        let header = {}
        let transactions = []
        if(doc_type === 'PO'){
            header['location'] = $('#loc').val()
            header['supplier'] = $('#supplier').val()
            header['remarks'] = $('#remarks').val()
            header['taxable'] = $('#taxable').val()
            header['owner'] = $('#owner').val()
        }

        // append transactions
        let rowcount = $('#tBody tr').length

        if(rowcount > 0){
            // rowcount += 1

            let validate = productMaster.validateTransactions()
            if(validate['err_count'] > 0 )
            {
                Swal.fire({
                    'icon':'error',
                    'html':validate['message']
                })
            }
            else {
                let rows = $('#tBody tr')
                for (let row = 1; row <= rowcount ; row++) {
                    // define ids
                    let barcode, pack_qty,tran_qty,unit_cost,total_cost,packing
                    packing = $(`#packing_${row} option:selected`)
                    barcode = $(`#barcode_${row}`)
                    pack_qty = $(`#pack_qty_${row}`)
                    tran_qty = $(`#tran_qty_${row}`)
                    unit_cost = $(`#unit_cost_${row}`)
                    total_cost = $(`#total_cost_${row}`)

                    let tran = {
                        "line":row,"barcode":barcode.text(),"packing":packing.text(),"pack_qty":pack_qty.val(),
                        "tran_qty":tran_qty.val(),"cost":unit_cost.val(),"total_cost":total_cost.val()

                    }

                    transactions.push(tran)
                }

                let data = {
                    'module':'document','data':{"header":header,"doc_type":doc_type,"transactions":transactions}
                }
                let send = api.put(data)
                if(send['status_code'] ===  202){
                    location.href = '/'
                } else {
                    alert(send['message'])
                }


            }


        }


    }

    // View
    view(doc_type,entry){
        let data = {
            "module":"document",
            "data":{
                "doc":doc_type,
                "entry":entry,
                "mac":"C4:9D:ED:93:4B:BC"

            }
        }

        let fetch = api.view(data)
        let status = fetch['status_code']

        if(status === 200){
            // access values
            let response = fetch['message']
            let header,trans
            header = response['header']
            $('#ent_num').val(header['pk'])
            $('#supplier').val(header['supplier']['id'])
            $('#loc').val(`${header['location']['loc_id']} - ${header['location']['descr']}`)
            $('#ent_date').val(header['date'])
            $('#t_owner').val(header['owner'])
            $('#taxable').val(header['taxable'])

            let extra = header['extras']
            $('#taxable_amt').val(extra['taxable_amount'])

            $('#tot_amt').val(extra['total'])
            $('#ent_rm').val(header['remarks'])

            let tax = extra['tax']
            let vat = tax['tax_vat']
            $('#taxable_amt').val(tax['taxable_amt'])
            $('#tax_amt').val(vat)

            console.table(extra)
            trans = response['trans']
            let tr = ''
            for (let t = 0; t < trans.length; t++) {
                let tran = trans[t]
                tr += `
                <tr id="row_1" class="pointer">
                                <td id="line_1">${tran['line']}</td>
                                <td id="barcode_1">${tran['product']['barcode']}</td>
                                <td id="descriptopn_1">${tran['product']['name']}</td>
                                <td id="packing_1">${tran['packing']}</td>
                                <td id="pack_qty_q">${tran['pack_qty']}</td>
                                <td id="tran_qty_1">${tran['qty']}</td>
                                
                                <td id="unit_cost_1">${tran['un_cost']}</td>
                                <td id="total_cost_1">${tran['tot_cost']}</td>
                            </tr>
                `

            }

            $('#tBody').html(tr)

        } else {
            al('info',fetch['message'])
        }
    }

}

const docs = new Docs()