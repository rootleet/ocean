
function log_issue(uni) {
    let log_title = `#log_title_${uni}`
    let log_body = `#log_body_${uni}`
    let issues_url = $('#issues_url').val()
    let error = 0;

    if(!str_len($(log_title).val()) || !str_len($(log_body).val()) || !str_len(issues_url))
    {
        swal_response('error','Invalid Form','Please fill all required fields')
    } else
    {
        let form_date = {
            'issue':uni,
            'title':$(log_title).val(),
            'body': $(log_body).val()

        }

        $.ajax({
            url:issues_url,
            type:'GET',
            data:form_date,
            success: function (response) {
                error_handler(response)
            }
        })
    }


}

function api_call(module,action,data) {
    // console.log(JSON.stringify(data))
    let link = `/adminapi/${module}/${action}/`
    console.table(data)
    var result = 0;
    $.ajax({
        url:link,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        processData: false,
        async: false,
        dataType: 'html',
        data:JSON.stringify(data),
        // dataType: "json",
        success: function (response) {

            result =  response
            console.table(response)

        },
        error: function (error)
        {

            result = error
        }
    })

    console.table(result['responseText'])
    return result
}

function apiv2(module,action,data) {
    // console.log(JSON.stringify(data))
    let link = `/api/${module}/${action}/`
    // console.table(link)
    var result = 0;
    $.ajax({
        url:link,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        processData: false,
        async: false,
        dataType: 'html',
        data:JSON.stringify(data),
        // dataType: "json",
        success: function (response) {

            result =  response
            // console.table(response)

        },
        error: function (error)
        {

            result = error
        }
    })

    // console.table(result['responseText'])
    return result
}


function dataType(data) {

        console.table({
            'data':data,'type':typeof(data)
        })
    }



function mark_for_escalation(issue) {

    let url = $('#url').val()
    let form_date = {
        'issue':issue
    }
    $.ajax({
            url:url,
            type:'GET',
            data:form_date,
            success: function (response) {
                error_handler(response)
                console.log(response)
            }
        })
}

function new_adj_hd(data) {


    let exe = JSON.parse(api_call('adjustment', 'new_hd', data))
    let status = exe['status']
    let message = exe['message']

    return message;
}

function new_adj_tran(parent,line,product,packing,quantity,total) {
    let p = {'id':65}
    var data = {'parent':parent,"line":line,"product":product,"packing":packing,"quantity":quantity,"total":total}

    console.table(data)

    let exe =  JSON.parse(api_call('adjustment','new_tran',data))
    let status = exe['status']
    let message = exe['message']

    return status
}

async function escalate(provider_code) {
    const {value: text} = await Swal.fire({
        input: 'textarea',
        inputLabel: 'Message',
        inputPlaceholder: 'Type your message here...',
        inputAttributes: {
            'aria-label': 'Type your message here' 
        },
        showCancelButton: true
    })

    if (text) {
        var form_date = {
        'x_provider':provider_code,
            'email':$('#Email').html(),
            'subject':text
        }
        var url = $('#send_url').val()
        $.ajax({
            url:url,
            type:'GET',
            data:form_date,
            success: function (response) {
                swal_success(response)
            }
        })
        //Swal.fire(text)

    } else {
        await escalate(provider_code)
    }
}

async function close_issue(issue_id) {
    let url = $('#close_url').val()



    const {value: text} = await Swal.fire({
        input: 'textarea',
        inputLabel: 'Closing Remarks',
        inputPlaceholder: 'Type your message here...',
        inputAttributes: {
            'aria-label': 'Type your message here'
        },
        showCancelButton: true
    })

    if (text) {
        let form_data = {
        'entry': issue_id,'remarks':text
    }
        $.ajax({
                url: url,
                data: form_data,
                type: "GET",
                success: function (response) {
                    error_handler(response)
                    window.close()
                }
            })

    }




}


async function task_export(document) {
    const {value: doc_type} = await Swal.fire({
        title: 'Select field validation',
        input: 'select',
        inputOptions: {
            'pdf': 'PDF'
        },

        inputPlaceholder: 'Document Type',
        showCancelButton: true,
        // inputValidator: (value) => {
        //     return new Promise((resolve) => {
        //         if (value === 'oranges') {
        //             resolve()
        //         } else {
        //             resolve('You need to select oranges :)')
        //         }
        //     })
        // }
    })

    if (doc_type) {
        const inputOptions = new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              '0': 'Open',
              '1': 'Closed',
              '01': 'All'
            })
          }, 1000)
        })

        const { value: sort } = await Swal.fire({
          title: 'Select Sort',
          input: 'radio',
          inputOptions: inputOptions,
          inputValidator: (value) => {
            if (!value) {
              return 'You need to choose something!'
            }
          }
        })

        if (sort) {
            let url = $('#export_url').val();
            var form_date = {
                'sort':sort,
                'doc_type':doc_type
            }
            $.ajax({
                url:url,
                data:form_date,
                type:'GET',
                success: function (response) {
                    let spl = response.split('%%')
                    console.log(response)
                    if (spl[0] === 'done')
                    {
                        let text = `view <a target="_blank" href="/static/general/docs/${spl[1]}.pdf">file</a>`
                        swal_response('success','FILE READY',text)
                    } else {
                        alert("THERE IS AN ISSUE")
                    }
                }
            })
          Swal.fire({ html: `You selected: ${sort} Doc : ${doc_type}` })
        }
    }
}

function row_cal(id) {
    let pack_qty,qty,total



    pack_qty = parseFloat($(`#pack_${id}`).val())
    qty = parseFloat($(`#qty_${id}`).val())
    let result = pack_qty * qty
    total = $(`#total_${id}`)

    // console.log(`${pack_qty} ${qty}`)

    let calc = parseFloat(result)
    total.val(calc)

}

$(function() {
    $("#search_task").on("change paste keyup", function() {
       let query = $(this).val()

        let form_date = {
           'for':'task',
            'query':query
        }

        if(query.length > 0)
        {
            $.ajax({
            url:$('#search_url').val(),
            data:form_date,
            type: 'GET',
            success: function (response) {
                console.log(response)
                let res = response
                let this_row;
                let link_res = ""
                for (let i = 0; i < res.length; i++) {
                    this_row = res[i]['fields']
                    link_res += `<a href="/task/${this_row.entry_uni}/view/" class="list-group-item">${this_row.title}</a>`
                }
                $('#searchRes').html(link_res)
            }
        })
        } else {
            $('#searchRes').html('')
        }


    });
});

//below is adjustment functions

$(function() {
    $("#product_list").on("change paste keyup", function() {
        let query = $(this).val()
        let doc = $('docType').val()

        productMaster.productsPreview()

        let form_date = {
           'for':'item_for_adjust',
            'query':query
        }

        if(query.length > 0)
        {
            $.ajax({
            url:$('#search_url').val(),
            data:form_date,
            type: 'GET',
            success: function (response) {
                console.log(response)
                let res = response
                let this_row;
                let link_res = ""
                for (let i = 0; i < res.length; i++) {
                    this_row = res[i]['fields']
                    link_res += `<div class="list-group-item d-flex flex-wrap"> <button  onclick="add_adj_tran_list('${this_row.barcode}')" class="btn btn-sm btn-info">ADD</button> ${this_row.barcode} | ${this_row.descr}</div>`
                }
                $('#searchRes').html(link_res)
            }
        })
        } else {
            $('#searchRes').html('')
        }
    })
}
)



function add_adj_tran_list(barcode) {
    let product,packing,p_descr,this_pack=''
    //get product details
    product = JSON.parse(pClass.GetProduct(barcode))[0]['fields']
    p_descr = product.shrt_descr

    // check if barcode exist
    let rows = $('#tBody tr').length
    let exist = 0;

    for (let i = 0; i <= rows; i++) {
        let line_barcode = `#barcode_${i}`
        let barcode_val = $(line_barcode).val()
        //console.log(barcode_val)
        if (barcode_val == barcode)
        {
            exist = 1;
        }
    }
    console.log(exist)

    if(exist === 0)
    {
        let rows =+ 1
        // get packing details
        packing = JSON.parse(pClass.GetProductPacking(barcode))
        let options = ''
        for (let i = 0; i < packing.length; i++) {
            this_pack = packing[i]['fields']
            let packing_type = this_pack['packing_type']
            let pack_qty = this_pack['pack_qty']
            let this_option = `<option value="${pack_qty}">${packing_type}</option>`
            options += this_option
        }


        let qty_id = `qty_${rows}`
        let barcode_id = `barcode_${rows}`
        let pack_qty = `pack_${rows}`
        let total = `total_${rows}`
        let tr = `<tr id="row${rows}">
        
                                    
                                    <td><input id="${barcode_id}" type="text" class="form-control form-control-sm rounded-0" readonly value="${barcode}"></td>
                                    <td><input type="text" class="form-control form-control-sm rounded-0" readonly value="${p_descr}"></td>
                                    <td><select  class="form-control form-control-sm rounded-0" name="" id="${pack_qty}">${options}</select></td>
                                    <td><input onkeyup="row_cal(${rows})" id="${qty_id}" value="0" class="form-control form-control-sm rounded-0" type="number"></td>
                                    <td><input id="${total}" readonly value="0" class="form-control form-control-sm rounded-0" type="number"></td>
                                </tr>`

        $('#tBody').append(tr)

        // ctable(product)
        // ctable(packing)
        // ctable(options)
    }




    // add to row

}

function save_adjustment() {

    let remarks,rows,row_id,qty_id,total_id,loc;

    // check adjustment header
    remarks = $('#remarks').val()
    loc = $('#loc').val()

    if(remarks.length > 0 && loc.length > 0 )
    {

        // check each row to make sure row pass
        rows = $('#tBody tr').length

        if(rows > 0){
            let tran_err_count = 0;
            let tran_err_msg = 'error%%'
            // loop through each row to make sure no 0 values
            for (let i = 0; i < rows; i++) {

                let qty,total

                // get row ids
                qty_id = `#qty_${i}`
                row_id = `#row_${i}`
                total_id = `#total_${i}`

                qty = $(qty_id).val()
                total = $(total_id).val()


                if(total == 0)
                {
                    // append quantity error
                    tran_err_count ++
                    tran_err_msg += `<p>line number ${row_id}  : Cannot Make adjustment of 0</p>`
                }
            }

            if(tran_err_count > 0)
            {
                error_handler(tran_err_msg)
            }
            else
            {
                //insert into adjustment hd

                paren = new_adj_hd({'remark': remarks,'loc':loc})

                if( 1 > 0)
                {
                    console.log('NO ERROR')
                    console.log(rows)
                    for (let xi = 1; xi <= rows; xi++)
                    {
                        // todo insert each line
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

                        ctable([xi,barcode,pack,qty,total])

                        new_adj_tran(paren,xi,barcode,pack,qty,total)
                    }

                    // reload page
                    location.href='/inventory/adjustment/'

                } else {
                    error_handler(`error%%Cannot Create Header ${paren}`)
                }




            }

        } else {
            swal_response('error','Cannot Proceed','Document body cannot be empty, please add an item to list')
        }


    } else
    {
        error_handler(`error%%Please remarks can't be empty`)

    }


    // check adjustment transactions for error

}



    const isJson = (str) => {
      try {
          JSON.parse(str)
          return true
      } catch (e) {
          return false
      }
    }

const alert = (str) => {
    Swal.fire(str)
}