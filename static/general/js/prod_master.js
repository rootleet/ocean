


function getty(){

    var action_url = $('#autos_url').val()

    if (action_url.length < 1)
    {
        error_handler(`error%%Invalid Url`)
    }
    else
    {
        let value = $('#group').val()
        var form_data = {
            'function':'prod_subs',
            'group':value
        }

        console.log(form_data)

        var opts = '';

        $.ajax({
            type: "GET",
            url: action_url,
            data: form_data, // serializes the form's elements.
            success: function(response)
            {
                for (let i = 0; i < response.length; i++) {
                    let this_resp = response[i].fields
                    let this_pk = response[i].pk
                    opts += `<option value="${this_pk}">${this_resp.descr}</option>`
                    // ctable(this_resp)
                }
                ctable(opts)

                $('#sub_group').html(opts)
                $('#sub_group').prop('disabled', false)
            }
        });


    }

}

function barcode_x() {
    var bcode_set = $('#bcode_set').val()

    if(bcode_set === '1'){
        $('#bcode').prop('disabled',false)

        $('#bcode').val('')
    }
}