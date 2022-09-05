function swal_reload(message='')
{
    Swal.fire({

        icon: 'success',
        title: 'RELOAD',
        text:message,
        showDenyButton: false,
        showCancelButton: false,
        confirmButtonText: 'OK',
        denyButtonText: `Don't save`,
    }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.isConfirmed) {
            location.reload()
        } else if (result.isDenied) {
            location.reload()
        }
    })
}

function swal_success(str) {
    swal.fire({
        icon: 'success',
        title: 'Process Completed Successfully',
        text:str,
    })
}

function swal_response(icon='info',title = 'SWAL RESPONSE',text ='') {
    swal.fire({
        icon: icon,
        title: title,
        text:text,
    })
}

// error handler
function error_handler(response)
{
    // split response
    if(response.split('%%').length === 2)
    {
        let response_split = response.split('%%');
        let response_type = response_split[0];
        let response_message = response_split[1];
        console.log(response)
        // $('#gen_modal').modal('hide')
        // switching response type
        switch (response_type)
        {
            case 'done':
                switch (response_message){
                    case 'msg_sent':
                        $('#convo_message').val('')
                        load_convo_message()
                        break;
                    default:
                        swal_reload("Process Completed")
                        console.table(response_message)
                        break;
                }
                break

            case 'error':
                swal_response('error','PROCEDURE ERROR',response_message)
                break;
            default:
                swal_response('error','CONTACT SYSTEM ADMINISTRATOR',response_message)
        }

    }
}

function str_len(str) {
    if(str.length > 0)
    {
        return true
    } else
    {
        return false
    }
}

function ctable(str){
    console.table(str)
}

function clog(str) {
    console.log(str)
}