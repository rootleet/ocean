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
        // $('#gen_modal').modal('hide')
        // switching response type
        switch (response_type)
        {
            case 'done':
                swal_response('success','PROCEDURE COMPLETED',response_message)
                break;
            case 'error':
                swal_response('error','PROCEDURE ERROR',response_message)
                break;
            default:
                swal_response('error','CONTACT SYSTEM ADMINISTRATOR',response_message)
        }

    }
}