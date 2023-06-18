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
                    packing = $(`#packing_${row}`)
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
}

const docs = new Docs()