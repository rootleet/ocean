class Sms {

    // start of getting all sms apis
    getApi(id='*'){
        let data = {"sender_id":id}
        return apiv2('sms', 'getApis', data)
    }
    // end of getting all sms apis

    // start of getting queued sms
    sms(sms_id='*'){
        let data = {"sms_id":sms_id}
        return apiv2('sms', 'getMessages', data)
    }
    // end of getting queued sms

    // start of loading sms apis to screen
    loadScreen(){

        if(isJson(this.getApi()))
        {
            // valid json
            let response = JSON.parse(this.getApi())
            let st,msg

            st = response['status']
            msg = response['message']

            let tr = ''
            if(st === 200)
            {
                // there is record
                for (let ap = 0; ap < msg.length; ap++) {
                    let pk,api_desc,api_key,sender_id,status,timestamp,clean_timestamp, api = msg[ap]

                    pk = api['pk']
                    api_desc = api['api_desc'];
                    api_key = api['api_key'];
                    sender_id = api['sender_id'];
                    status = api['status'];
                    timestamp = api['timestamp'];
                    clean_timestamp = `${timestamp['date']} ${timestamp['time']}`;


                    tr += `<tr>
                                            <td>${sender_id}</td>
                                            <td>${api_desc}</td>
                                            <td><div class="w-100 d-flex flex-wrap">
                                                <button onclick="sms.DelSmsApi('${api_key}')" class="btn btn-sm btn-danger rounded-0">DEL</button>
                                                <button onclick="sms.EditSmsApi('${api_key}')" class="btn btn-sm btn-warning rounded-0">EDIT</button>
                                            </div></td>
                                        </tr>`;

                }
            }

            $('#smsTble').html(tr)

        } else
        {
            $('#smsBody').html(`
                <div class="w-100 h-100 d-flex flex-wrap align-content-center justify-content-center">
                <div class="alert alert-info">NO SMS API</div>
                </div>
            `)
        }
    }
    // end of loading sms apis to screen
    EditSmsApi(pk){
        alert(`Update ${pk}`)
    }

    DelSmsApi(pk){
        alert(`Deleting ${pk}`)
    }

    // start of que a sms
    QueSMS(){
        let api,to,message,err_c = 0,err_m = ''

        api = $('#api').val()
        to = $('#to').val()
        message = $('#message').val()

        if(api.length < 0)
        {
            err_c ++
            err_m += ` | INVALID API KEY ${api}`
        }
        if(to.length < 0)
        {
            err_c ++
            err_m += ` | INVALID RECIPIENT ${to}`
        }
        if(message.length < 0)
        {
            err_c ++
            err_m += ` | INVALID MESSAGE ${message}`
        }

        if(err_c > 0)
        {
            // there is an error
            swal_response('error','PROCEDURE ERROR',err_m)
        } else {
            // api call
            let data = {'api':api,'to':to,'message':message}
            let api_response = apiv2('sms','que',data)

            if(isJson(api_response)){
                let xxl = JSON.parse(api_response)
                swal_response('info',xxl['status'],xxl['message'])
                $('#newSMS').modal('hide')
                $('#api').val('')
                $('#to').val('')
                $('#message').val('')
            } else {
                swal_response('error',"UNCOMPLETED TRANSACTION",`API returned an invalid json ${api_response}`)
            }
        }



    }
    // end of que a sms



}

const sms = new Sms()