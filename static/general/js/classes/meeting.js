class Meeting {


    constructor() {
        let base_url = '/apiv2/meeting/'
    }
    saveMeeting(){
        let top_gees = ['title','descr','start_date','start_time','end_date','end_time','owner']

        if (anton.validateInputs(top_gees)) {

            let data = {}
            data['stage'] = 'new_meeting'
            data['title'] = $('#title').val()
            data['descr'] = $('#descr').val()
            data['start_date'] = $('#start_date').val()
            data['start_time'] = $('#start_time').val()
            data['end_date'] = $('#end_date').val()
            data['end_time'] = $('#end_time').val()
            data['owner'] = $('#owner').val()

            let payload = {
                data: data
            }

            let contacts_length = $('#contacts legend')
            // console.log(contacts_length.html())
            let contacts = []
            for (let c = 0; c < contacts_length.length; c++) {

                let x_id = $(`#contact_r${c + 1}`)

                if (x_id.is(":checked")) {
                    var value = x_id.val();
                    contacts.push(value)
                }
            }

            let issues = []
            let issue_cont = $('#vals_container tr');
            for (let issue_index = 0; issue_index < issue_cont.length; issue_index ++)
            {
                let issue_id = issue_index + 1
                let issue = $(`#iss_${issue_index}`).text()
                issues.push(issue)
            }


            payload['data']['contacts'] = contacts
            payload['data']['issues'] = issues

            let response = api.call('PUT',payload,'/apiv2/meeting/')
            if(response['status_code'] === 200){
                kasa.confirm(response['message'],1,'/meeting/')
            } else {
                kasa.error(response['message'])
            }


            console.table(payload)
        } else {
            kasa.warning("FILL ALL REQUIRED FIELDS")
        }
    }

    NewMeetingTran(){
        let talking_point = $('#talking_point').val()
        let tran_text = $('#tran_text').val()
        let meeting = $('#meetingPk').val()

        if(talking_point !== 'null' && tran_text.length > 0)
        {
            let data = {
                'meeting':meeting,'talking_point':talking_point,'tran':tran_text
            }

            let apicall = api_call('meeting','tran',data)

            let jr = JSON.parse(apicall)
            console.table(jr)

            if(jr['status'] === 200)
            {
                this.liveTrans()
            }


        } else {

            error_handler('error%%Male Sure talking point is selected and also data is enterted')
        }


    }

    liveTrans(){
        let meeting = $('#meetingPk').val()
        let apicall = api_call('meeting','GrtTan',{'meeting':meeting})
        let jr = JSON.parse(apicall)


        if(jr['status'] === 200)
        {
            let m = jr['message']
            let ht = ""
            // console.table(m)
            for (let i = 0; i < m.length; i++) {
                let r = m[i]
                let point,descr,created_date,created_time,owner
                point = r['point']
                descr = r['descr']
                created_date = r['created_date']
                created_time = r['created_time']
                owner = r['owner']

                ht += `<div class="alert alert-primary">
                                                <strong>${point}</strong> <br>
                                                <p class="m-0">${descr}</p>
                                            </div>`

                console.table(r)
                console.log(point)
                $('#xBody').html(ht)
            }
        }

    }

    startMeeting(uni = '') {
        let payload = {
            'module':'start_meeting',
            data:{
                'uni':uni
            }
        }

        let response = api.call('PATCH',payload,'/apiv2/meeting/')
        console.log(response)
        if(response['status_code'] === 200){
            kasa.confirm("MEETING STARTED",1,`/meeting/config_meeting/${uni}/`)
        } else {
            kasa.warning(response['message'])
        }

        // if(confirm("Are you sure you want to start meeting"))
        // {
        //     let apcall = api_call('meeting','start',{'meeting':$('#meetingPk').val()})
        //     let r = JSON.parse(apcall)
        //
        //     if(r['status'] === 200)
        //     {
        //         location.reload()
        //     } else {
        //         error_handler('error%%Could Not Start Meeting')
        //     }
        // }
    }

    endMeeting(uni) {


        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, end it!'
        }).then((result) => {
            if (result.isConfirmed) {


                tinyMCE.triggerSave();
                let payload = {
                    'module':'end_meeting',
                    data:{
                        'uni':uni,
                        document:$('.tinymce-editor').val()
                    }
                }

                let response = api.call('PATCH',payload,'/apiv2/meeting/')
                console.log(response)
                if(response['status_code'] === 200){
                    var currentPageUrl = window.location.href;

                    kasa.confirm("MEETING ENDED",1,currentPageUrl)
                } else {
                    kasa.warning(response['message'])
                }

            } else {
                Swal.fire({
                    title: 'Operation canceled',
                    icon: 'info'
                });
            }
        });

    }

    newTalkingPoint(uni) {

        Swal.fire({
          title: 'ADDING PARTICIPANT',
          input: 'text',
          inputLabel: 'Enter your input:',
          showCancelButton: true,
          cancelButtonText: 'Cancel',
          confirmButtonText: 'Validate',
          showLoaderOnConfirm: true,
          preConfirm: (input) => {
            // Perform input validation here
            if (input.trim() === '') {
              Swal.showValidationMessage('Input cannot be empty');
            } else {
              return input;
            }
          },
          allowOutsideClick: () => !Swal.isLoading()
        }).then((result) => {
          if (result.isConfirmed) {
            kasa.info("HELLO")
          }
        });


    }

    viewAttach(meeting){
        let payload = {}
        let data = {}
        payload['module'] = 'meetings'
        data['part'] = 'single';
        data['key'] = meeting
        payload['data'] = data

        let response = api.call('VIEW',payload,'/apiv2/meeting/')
        console.table(response)
        amodal.setTitleText("ATTACHMENTS")
        let html = ''
        if(response['status_code'] === 200){
            let attachments = response['message'][0]['attachments']
            let meeting = response['message'][0]
            if(attachments.length > 0){
                let tr = ''
                for (let at = 0; at < attachments.length; at++) {
                    let attachment = attachments[at]
                    tr += `<tr><td><i class="bi bi-file text-info"></i> ${attachment['name']}</td><td><i class="pointer bi bi-trash-fill text-danger" onclick="kasa.info('Pending Feature')" title="Delete"></i></td></tr>`
                }
                html = `<table class="table table-sm">${tr}</table>`
            } else {
                html = "NO ATTACHMENTS"
            }
            let form = `<form method="post" action="/meeting/attach/" enctype="multipart/form-data" class="modal-body">
                                                
                                                <input type="hidden" name="cryp_key" value="${meeting['pk']}">
                                                <input type="hidden" value="MET" name="doc">
                                                <div class="custom-file mb-3">
                                                  <input type="file" class="custom-file-input" id="customFile" name="media">
                                                </div>

                                              
                                            <button class="btn btn-success" type="submit">SAVE</button>

                                           </form> <hr> ${html}
`
            html = `${form}`
        } else {
            html = response['message']
        }
        amodal.setBodyHtml(html)

        amodal.show()
    }

    reportForm(){
        let form = `<div class="w-50 p-2 shadow mx-auto">
                        <label for="start_date" class="w-100 text-info">Date From <small class="text-danger">*</small></label>
                        <input type="date" id="start_date" class="form-control w-100 form-control-sm mb-2">
                        <label for="end_date" class="text-info">Date To <small class="text-danger">*</small></label><br>
                        <input type="date" id="end_date" class="form-control form-control-sm mb-2">
                        <label for="status" class="text-info">Status</label><br>
                        <select id="status" name="status" class="form-control form-control-sm mb-2">
                                <option value="*">All</option>
                                <option value="0">Pending</option>
                                <option value="1">Live</option>
                                <option value="3">Close</option>
                        </select>
                        
                        <label for="document" class="text-info">Document</label><br>
                        <select id="document" name="document" class="form-control form-control-sm mb-2">
                                <option value="view">Preview</option>
                                <option value="excel">EXCEL</option>
                                <option disabled value="pdf">PDF</option>
                        </select>
                        
                        <button onclick="meeting.report()" class="btn btn-info w-100">SUBMIT</button>
                    </div>`
        card.setBody(form)
        card.setTitle("MEETINGS REPORT")
    }

    report(){

        // validate fields
        let fields = ['start_date','end_date','status','document']
        if(anton.validateInputs(fields)){
          // get fields
            let start_date,end_date,status,document;
            start_date = $('#start_date').val()
            end_date = $('#end_date').val()
            status = $('#status').val()
            document = $('#document').val()

            let data = {};
            data['start_date'] = start_date
            data['end_date'] = end_date
            data['status'] = status
            data['document'] = document;

            let payload = {
                module:'header',
                data:data
            };

            let response = api.call('VIEW',payload,'/meeting/reports/');

            let html = '';

            if(response['status_code'] === 200){
                    let header, message, count, transactions
                    message = response['message'];

                    if(document === 'view') {
                        header = message['header'];
                        count = header['count'];
                        transactions = message['transactions']
                        // console.table(transactions)
                        if (count > 0) {

                            let tr = ''

                            for (let me = 0; me < count; me++) {
                                let attachments, participants, points, meeting = transactions[me]
                                let times = meeting['start_end'];
                                let owner = meeting['owner'];
                                let duration = `${times['start_date']} ${times['start_time']} to ${times['end_date']} ${times['end_time']}`;
                                let stat = meeting['m_stat']

                                tr += `<tr><td>${meeting['title']}</td><td>${duration}</td><td>${owner['full_name']}</td><td><kbd class="${stat['class']}">${stat['text']}</kbd></td></tr>`

                            }

                            html = `<table class="table table-sm datatable table-bordered"><thead><tr><th>Title</th><th>Duration</th><th>OWNER</th><th>STATUS</th></tr></thead>
                        <tbody>${tr}</tbody></table>`

                        } else {
                            html = `<div class="w-100 h-100 d-flex flex-wrap justify-content-center align-content-center">
                            <div class="alert alert-danger">NO DATA</div>
                        </div>`
                        }
                    } else if (document === 'excel'){
                        kasa.html(`<a href="/${message}">DOWNLOAD FILE</a>`)
                    }

                }
            else {
                    html = `<div class="w-100 h-100 d-flex flex-wrap justify-content-center align-content-center">
                            <div class="alert alert-danger">There is an error loading data ${response['message']}</div>
                        </div>`
                }

            $('#reportCardBody').html(html)


        }
        else{
            kasa.warning("FILL ALL REQUIRED FIELDS")
        }


    }


    viewParticipants(meeting) {
        let payload = {}
        let data = {}
        payload['module'] = 'meetings'
        data['part'] = 'single';
        data['key'] = meeting
        payload['data'] = data

        let response = api.call('VIEW',payload,'/apiv2/meeting/')


        amodal.setTitleText("PARTICIPANTS")

        let participants = response['message'][0]['participants']
        let tr = ''
        for (let at = 0; at < participants.length; at++) {
            let participant = participants[at]
            tr += `<tr><td><i class="bx bx-user-circle text-info"></i> ${participant['name']}</td><td><i class="pointer bi bi-trash-fill text-danger" onclick="kasa.info('Pending Feature')" title="Delete"></i></td></tr>`
        }
        let html = `<table class="table table-sm">${tr}</table>`
        amodal.setBodyHtml(html)
        amodal.show()
        console.table(participants)
    }
}

const meeting = new Meeting();
// alert("MEETINGS JS LOADED")