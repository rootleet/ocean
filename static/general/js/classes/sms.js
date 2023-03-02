class Sms {

    async newSms() {
        /* inputOptions can be an object or Promise */
        const inputOptions = new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    '1': 'Single',
                    '2': 'Multiple',
                })
            }, 1000)
        })

        const {value: choice} = await Swal.fire({
            title: 'Recipient Type',
            input: 'radio',
            inputOptions: inputOptions,
            inputValidator: (value) => {
                if (!value) {
                    return 'You need to choose something!'
                }
            }
        })

        if (choice) {

            // get sms api
            let av_api = this.getApi('*')

            if(isJson(av_api))
            {
                let status,message,resp

                resp = JSON.parse(av_api)
                status = resp['status']
                message = resp['message']

                if(status === 200)
                {

                    let options = ''
                    let html = ''
                    for (let ap = 0; ap < message.length; ap++) {
                        let this_ap = message[ap]
                        // ctable(message[ap])
                        options += `<option value="${this_ap['pk']}">${this_ap['sender_id']}</option>`
                    }

                    console.log(options)

                    if(choice == '1')
                    {

                        Swal.fire({html:"Send Single"})

                        html += `<label for="api">API</label><select id="api" class="form-control rounded-0 mb-2">${options}</select>
                                <input placeholder="recipient" id="to" class="form-control rounded-0 mb-2" type="tel" required /> 
                                <textarea placeholder="Message" id="message" class="form-control mb-2 rounded-0" rows="5"></textarea>
                                <button class="btn btn-sm btn-success" onclick="sms.QueSMS()">SEND</button>`
                        Swal.fire({html:html,title:"Send SMS"})


                    } else if(choice == '2'){

                        $('#bulkSms').modal('show')

                    } else
                    {

                        Swal.fire({html: `You selected: ${choice}`})

                    }

                } else
                {
                    Swal.fire({html:"Wrong API Response"})
                }

            } else {
                Swal.fire({html:"API response is not a valid JSON"})
            }



        }
    }

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

    // server status
    ServerStatus()
    {
        if(isJson(apiv2('sms','servStat',{'null':null})))
        {
            let sstat = JSON.parse(apiv2('sms','servStat',{'null':null}))
            let status,message

            status = sstat['status']
            message = sstat['message']

            if(status === 200)
            {
                let sent,pending
                sent = message['sent']
                pending = message['pending']

                document.addEventListener("DOMContentLoaded", () => {
                    echarts.init(document.querySelector("#trafficChart")).setOption({
                        tooltip: {
                            trigger: 'item'
                        },
                        legend: {
                            top: '5%',
                            left: 'center'
                        },
                        series: [{
                            name: 'SMS Status',
                            type: 'pie',
                            radius: ['40%', '70%'],
                            avoidLabelOverlap: false,
                            label: {
                                show: true,
                                position: 'center'
                            },
                            emphasis: {
                                label: {
                                    show: true,
                                    fontSize: '18',
                                    fontWeight: 'bold'
                                }
                                },
                            labelLine: {
                                show: false
                            },
                            data: [{
                                value: pending,
                                name: 'Pending',
                            },
                                {
                                    value:sent,
                                    name: 'Sent'
                                }
                                ]
                        }]
                    });
                });

            }

        }

    }
    // server status

    // start of loading sms apis to screen
    loadApisScreen(){

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

    // loading sms scree
    loadSmsScreen(){
        let tr = ''
        let modals = ''
        if(isJson(this.sms('*')))
        {
            let all_sms = JSON.parse(this.sms('*'))

            let status,message
            status = all_sms['status']
            message = all_sms['message']

            if(status === 200)
            {

                // response is valid
                for (let mi = 0; mi < message.length; mi++) {
                    let msg = message[mi]
                    let from,to,mess,timestamp,status,last_tried,status_htm
                    from = msg['api']['sender_id']
                    to = msg['to']
                    mess = msg['message']
                    status = msg['status']
                    timestamp = `${msg['timestamp']['created_date']} ${msg['timestamp']['created_time']}`
                    last_tried = `${msg['timestamp']['tried_date']} ${msg['timestamp']['tried_time']}`

                    if(status === 1)
                    {
                        status_htm = `<small class="text-success">sent</small>`
                    } else {
                        status_htm = `<small class="text-info">pending</small>`
                    }

                    tr += `
                        <tr data-bs-target="#msag${mi}" data-bs-toggle="modal">
                                            <td>${from}</td>
                                            <td>${to}</td>
                                            <td>${timestamp}</td>
                                            <td>${status_htm}</td>
                                        </tr>
                                        
                    `

                    modals += `<div class="modal fade" id="msag${mi}" backdrop="false">
                                            <div class="modal-dialog">
                                                <div class="modal-content">
                                                    <div class="modal-header">
                                                        <h5 class="modal-title">
                                                            From ${from} to ${to}
                                                        </h5>
                                                    </div>

                                                    <div class="modal-body">

                                                        <div class="w-100 mb-2 container">
                                                            <div class="row w-100">
                                                                <div class="col-sm-4">
                                                                    <button class="btn btn-success">STATUS</button>
                                                                </div>
                                                                <div class="col-sm-8">
                                                                    <div class="w-100"><small class="w-100"><span>Queued On : </span><i class="text-info">${timestamp}</i></small></div>
                                                                    <div class="w-100"><small class="w-100"><span>Last Tried :</span><i class="text-info">${last_tried}</i></small></div>
                                                                </div>

                                                            </div>
                                                        </div>

                                                        <hr>

                                                        <div class="card">

                                                            <div class="card-body">
                                                                <h5 class="card-title">Message</h5>
                                                                <p>
                                                                ${mess}
                                                                </p>

                                                            </div>
                                                        </div>
                                                    </div>

                                                </div>
                                            </div>
                                        </div>`

                }

            } else {
                swal_response('warning',status,message)
                tr = message
            }

        } else {
            swal_response('error','PROCEDURE ERROR',`Response for all sms is not a valid Json`)
            tr = 'There response is an invalid JSON'
        }

        $('#smsBody').html(tr) // append modals
        $('#smsBody').append(modals) // append modals

    }
    // loading sms screen

    // load all screens
    loadAllSmsScreens()
    {

        this.loadSmsScreen();
        this.ServerStatus();
        this.loadApisScreen();
    }
    // end load all screens

}

const sms = new Sms()