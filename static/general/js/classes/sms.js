class Sms {
    getApi(id='*'){
        let data = {"sender_id":id}
        return apiv2('sms', 'get', data)
    }

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
                                                <button class="btn btn-sm btn-danger rounded-0">DEL</button>
                                                <button onclick="sms.EditSmsApi('${pk}')" class="btn btn-sm btn-warning rounded-0">EDIT</button>
                                            </div></td>
                                        </tr>`;

                }
            }

            $('#smsTble').html(tr)

        } else
        {
            swal_response("warning","","Invalid Response for sms load screen")
        }
    }

    EditSmsApi(pk){
        alert(`Update ${pk}`)
    }
}

const sms = new Sms()