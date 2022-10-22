
class Adjustment {

    loadScreen(pk){
        var data = {'pk': pk}
        let hd = JSON.parse(api_call('adjustment','get_hd',data))['message']
        let tran = JSON.parse(api_call('adjustment','get_tran',data))

        if(hd['status'] === 0)
        {
            // not processed
            $('#adjProcess').val(parseInt(pk))
            $('#adjProcess').prop( "disabled", false );

        } else
        {
            $('#adjProcess').prop( "disabled", true );
        }

        if(hd['next_count'] > 0)
        {
            // there is next
            $('#next').val(parseInt(hd['next']))
            $('#next').prop( "disabled", false );
        }
        else
        {
            //disable next
            $('#next').prop( "disabled", true );
        }

        if(hd['prev_count'] > 0)
        {
            // there is previous

            $('#prev').val(parseInt(hd['prev']))
            $('#prev').prop( "disabled", false );
        }
        else
        {
            // disable previous
            $('#prev').prop( "disabled", true );
        }

        $('#ent_date').val(hd['date'])
        $('#ent_num').val(hd['entry_no'])
        $('#ent_rm').val(hd['remark'])

        // console.table(hd)
        console.table(hd)
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

    approveAdjustment(pk)
    {
        if(confirm('Are you sure you want to approve document?'))
        {
            var data = {'pk': pk}
            let adjust = JSON.parse(api_call('adjustment','approve',data))

            console.table(adjust)

            let stat,msg
            stat = adjust['status']
            msg = adjust['message']

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