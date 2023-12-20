class Mailer {
    new_email_screen(){
                amodal.setTitleText("CREATE AN EMAIL");
                // get email senders
                let senders_payload = {
                    'module':'mail_senders',
                    data:{}
                };
                let senders_response = api.call('VIEW',senders_payload,'/adapi/')
                if(senders_response['status_code'] === 200){
                    let senders = senders_response['message'];
                    let senders_option = '';
                    for (let s = 0; s < senders.length; s++) {
                        let sender = senders[s];
                        senders_option += `<option value="${sender['pk']}">${sender['address']}</option>`
                    }


                    let form = `
                    <label for="sender">SENDER</label>
                    <select id="sender" class="form-control rounded-0 mb-2">${senders_option}</select>
                    <label for="recipient">RECIPIENT</label>
                    <input type="email" id="recipient" class="form-control rounded-0 mb-2">
                    <label for="cc">CC</label>
                    <input type="text" id="cc" class="form-control rounded-0 mb-2">
                    <label for="subject">SUBJECT</label>
                    <input type="text" class="form-control rounded-0 mb-2" id="subject">

                    
                    

                `;
                amodal.setBodyHtml(form);
                $('#sender').html(senders_option);
                $('#mailer_mailer').prepend(form);
                $('#mailer').modal('show');
                $('#mailer_footer').html(`<button onclick="mailer.que()" class="btn btn-success w-100">QUE</button>`)
                } else {
                    kasa.error(senders_response['message'])
                }


            }
    que() {
                let ids = ['sender','subject','recipient','cc','body'];
                if(anton.validateInputs(ids)){
                    let data = anton.Inputs(ids);
                    var fileInput = document.getElementById('attachment');
                    var file = fileInput.files[0];
                    if(file){
                        data['attachment'] = file
                    }
                    let payload = {
                        module:'que_mail',
                        data:data
                    };
                    console.table(payload)
                    let que = api.call('PUT',payload,'/adapi/');
                    Swal.fire({
                        icon:'success',
                        title:"Email Sent Successful",
                        html:`
                            <div style="width: 100%; text-align: left !important">
                            <strong>TO</strong> : ${data['recipient']} <br><br>
                            <strong>CC</strong> : ${data['cc']} <br><br>
                            <strong>Subject</strong> : ${data['subject']} <br><br>
                            <strong>Message</strong> : ${data['body']} <br><br>
                            </div>
                        `
                    })
                    return que
                } else {
                    kasa.error("ALL FIELDS REQUIRED")
                }
            }

    sync_mails(){
                loader.show();
                let payload = {
                    data:{
                        doc:'mail_sync_v2'
                    }
                };

                let sync = api.call('VIEW',payload,'/reports/api/');
                loader.hide()
                kasa.confirm(sync['message'],1,'here');
            }
}

const mailer = new Mailer();