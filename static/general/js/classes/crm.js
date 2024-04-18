class Crm {
    constructor() {
        let api_int = '/crm/api/';
    }
    newScreen(){
        let html = `
            <div class="container"><div class="row" style="height: 20vh">
                <div class="col-sm-6"><button class="btn btn-outline-info w-100 h-100">Follow Up</button></div>
                <div class="col-sm-6"><button onclick="crm.newLog()" class="btn btn-outline-success w-100 h-100">New Response</button></div>
            </div></div>
        `

        pop.setTitleText("Customer Response")
        pop.setBodyHtml(html)
        pop.show()
    }
    newLog(){
        let form = '';
        let sectors = this.getSector('*');
        if(anton.IsRequest(sectors)){
            // amake sectors
            let sec_options = `<option value="0">Select Sector</option>`
            let secs = sectors['message'];
            for(let sc = 0;  sc < secs.length; sc++){
                let sec = secs[sc];
                sec_options += `<option value="${sec['pk']}" >${sec['name']}</option>`
            }

            // get positions
            let positions = this.getPosition('*');
            if(anton.IsRequest(positions)){
                let posts = positions['message'];
                let post_options = `<options>Select Position</options>`;
                for(let po = 0; po < posts.length; po++){
                    let post = posts[po];
                    post_options += `<option value="${post['pk']}">${post['name']}</option>`
                }

                // create form now
                let sector = fom.select('sector',sec_options,'',true);
                let comp_name = fom.input('text','company_name','',true);
                let secomp = `<div class="row">
                                        <div class="col-sm-6">${sector}</div><div class="col-sm-6">${comp_name}</div>
                                    </div><hr>`

                let cont_per = fom.input('text','contact_person','',true);
                let pos = fom.select('position',post_options,'',true);
                let phone = fom.text('phone','',true);
                let email = fom.email('email','',true);
                let contact = `
                    <div class="row">
                        <div class="col-sm-6">${cont_per}</div><div class="col-sm-6">${pos}</div>
                        <div class="col-sm-6">${phone}</div><div class="col-sm-6">${email}</div>
                    </div><hr>
                `
                form += secomp;
                form += contact;
                //form += fom.select('sector',sec_options,'',true);
                //form += fom.input('text','company_name','',true);
                //form += fom.input('text','contact_person','',true);
                //form += fom.select('position',post_options,'',true);
                let flag = `<label class="text-info" for="flag">FLAG </label>
                <select id="flag" onchange="followUpCheck()" name="flag" class="form-control mb-2 rounded-0"><
                                    <option>Select Flag</option>
                                    <option value="success">Reachable</option>
                                    <option value="unreachable">Unreachable</option></select>`;

                console.log(flag)
                let f_date = `<div id="f_date"></div>`

                let ff = `
                    <div class="row"><div class="col-sm-6">${flag}</div><div class="col-sm-6">${f_date}</div></div><hr>
                `

                form += ff;

                let sub_options = `
                    <option value="Car Sales">Car Sales</option>
                    <option value="Spare Parts">Spare Parts</option>
                    <option value="Servicing">Serving</option>
                    <option value="Other">Others</option>
                `
                form += fom.select('subject',sub_options,'',true);
                form += fom.textarea('details',5,true);


                amodal.setTitleText("New Log");
                amodal.setBodyHtml(form);
                amodal.setFooterHtml(`<button onclick="crm.saveNewLog()" class="btn btn-success">SAVE</button>`)
                amodal.show()
                let follow = fom.date('follow_up_date','',true);
                    $('#f_date').html(follow)

            } else {
                kasa.response(positions)
            }
        } else {
            kasa.response(sectors)
        }
        // form += fom.select('section',"")
        // Swal.fire({
        //   html:
        //     '<div style="text-align: left !important" class="w-100">' +
        //       '<label for="sector">SECTOR</label>' +
        //       '<select id="sector" class="form-control mb-2 rounded-0">' +
        //       '<option value="Accounting">Accounting</option>\n' +
        //       '  <option value="Agriculture">Agriculture</option>\n' +
        //       '  <option value="Arts">Arts</option>\n' +
        //       '  <option value="Construction">Construction</option>\n' +
        //       '  <option value="Education">Education</option>\n' +
        //       '  <option value="Engineering">Engineering</option>\n' +
        //       '  <option value="Finance">Finance</option>\n' +
        //       '  <option value="Healthcare">Healthcare</option>\n' +
        //       '  <option value="Information Technology">Information Technology</option>\n' +
        //       '  <option value="Legal">Legal</option>\n' +
        //       '  <option value="Manufacturing">Manufacturing</option>\n' +
        //       '  <option value="Marketing">Marketing</option>\n' +
        //       '  <option value="Media">Media</option>\n' +
        //       '  <option value="Non-profit">Non-profit</option>\n' +
        //       '  <option value="Retail">Retail</option>\n' +
        //       '  <option value="Sales">Sales</option>\n' +
        //       '  <option value="Science">Science</option>\n' +
        //       '  <option value="Social Services">Social Services</option>\n' +
        //       '  <option value="Transportation">Transportation</option>' +
        //       '</select>' +
        //       '<label for="company">COMPANY NAME</label><input id="company" class="mb-2 form-control rounded-0"> <hr>' +
        //       '<label for="name">CONTACT PERSON</label><input id="name" class="form-control rounded-0 mb-2">' +
        //       '<label for="position">POSITION</label><select name="" id="position" class="form-control rounded-0 mb-2">' +
        //       '<option value="CEO">CEO</option>\n' +
        //       '  <option value="COO">COO (Chief Operating Officer)</option>\n' +
        //       '  <option value="CFO">CFO (Chief Financial Officer)</option>\n' +
        //       '  <option value="HR Manager">HR Manager</option>\n' +
        //       '  <option value="Operations Manager">Operations Manager</option>' +
        //       '<option value="Tranport Manager">Transport Manager</option>' +
        //       '<option value="Receptionist">Receptionist</option><option value="manager">Manager</option>' +
        //       '<option value="Others">Others</option>' +
        //       '</select>' +
        //     '<label for="phone">PHONE</label><input type="tel" id="phone" class="form-control rounded-0 mb-2" placeholder="Phone Number">' +
        //       '<label for="email">EMAIL ADDRESS</label><input id="email" value="none" type="email" class="form-control rounded-0 mb-2"><hr>' +
        //       '<label for="subject">SUBJECT</label><input id="subject" class="form-control rounded-0 mb-2">' +
        //     '<label for="flag">FLAG</label><select id="flag" class="form-control rounded-0 mb-2">' +
        //     '<option value="" disabled selected>Select an option</option>' +
        //     '<option value="success">SUCCESS</option>' +
        //     '<option value="uncreachable">UNREACHABLE</option>' +
        //     '</select>' +
        //     '<label for="description">DETAILS</label><textarea id="description" rows="5" class="form-control rounded-0 mb-2" placeholder="Details"></textarea></div>',
        //   focusConfirm: false,
        //   showCancelButton: true,
        //   confirmButtonText: 'Save',
        //   cancelButtonText: 'Cancel',
        //   preConfirm: () => {
        //     const name = document.getElementById('name').value;
        //     const subject = document.getElementById('subject').value;
        //     const flag = document.getElementById('flag').value;
        //     const phone = document.getElementById('phone').value;
        //     const description = document.getElementById('description').value;
        //     let sector = document.getElementById('sector').value;
        //     let email = document.getElementById('email').value;
        //     let position = document.getElementById('position').value;
        //     let company = document.getElementById('company').value;
        //
        //     if (
        //       !name ||
        //       !subject ||
        //       !phone ||
        //       flag === '' ||
        //       !description || !sector || !email || !position || !company
        //     ) {
        //       Swal.showValidationMessage('Please fill in all fields');
        //     }
        //
        //     // Return an object with the values of the input fields
        //     let x = {
        //       name: name,
        //       subject: subject,
        //       phone: phone,
        //       flag: flag,
        //       description: description,sector:sector,email:email,position:position,company:company
        //     };
        //
        //     return x;
        //
        //   },
        // }).then((result) => {
        //   if (result.isConfirmed) {
        //     let vals = result.value
        //     let data = {
        //         name:vals.name,
        //         subject:vals.subject,
        //         phone:vals.phone,
        //         flag:vals.flag,
        //         description:vals.description,
        //         mypk:$('#mypk').val(),
        //         company:vals.company,
        //         position:vals.position,
        //         email:vals.email,
        //         sector:vals.sector
        //     };
        //
        //     let payload = {
        //         'module':'log',
        //         data:data
        //     };
        //
        //     console.table(payload);
        //
        //     let lg = api.call("PUT",payload,'/crm/api/');
        //     location.reload()
        //     kasa.info(lg['message'])
        //
        //   }
        // });

    }

    newUser(){
        // Create an array of options for the select input
        let users = user.allUsers();
        if (users['status_code'] === 200){
            let msg = users['message'];
            let opt = {}
            for (let m = 0; m < msg.length; m++) {
                let tm = msg[m]
                opt[tm['pk']] = `${tm['fullname']} - ${tm['username']}`
            }

            console.table(opt)

            // Use SweetAlert 2 to create a modal with a select input
            Swal.fire({
              title: 'SELECT USER',
              input: 'select',
              inputOptions: opt,
              inputPlaceholder: 'Select an option',
              showCancelButton: true,
              cancelButtonText: 'Cancel',
              confirmButtonText: 'OK',
              inputValidator: (value) => {
                // Validate the selected option (optional)
                if (!value) {
                  return 'You must select an option!';
                }
              },
            }).then((result) => {
              if (result.isConfirmed) {
                const selectedOption = result.value;
                // Do something with the selected option
                // console.log(`You selected: ${selectedOption}`);
                let crmpayload = {
                    module:'add_user',
                    data:{
                        user:selectedOption
                    }
                };
                let crmUsAdd = api.call('PUT',crmpayload,'/crm/api/');
                // console.table(crmUsAdd)
                kasa.confirm(`${crmUsAdd['message']}`,1,'/crm/users/')
              }
            });
        }
        const options = ['Option 1', 'Option 2', 'Option 3'];



    }

    generateReports() {
        loader.show();
        let payload = {
            module:'generate_log_report',
            data:{}
        };

        kasa.confirm(
            api.call(
                'VIEW',
                payload,
                '/crm/api/')['message'],
            1,
            'here'
        )

        loader.hide()
    }

    uploadCsvScreen(){
        let html = `
        <a href="/static/general/crm-logs-reports/crm_upload_template.csv">Download Template</a><br>
        <label for="csv-file">Select CSV FILE</label>
        <input type="file" accept="text/csv" id="csv-file" class="form-control rounded-0 mb-2" >
        <button onclick="crm.uploadInCsv()" class="btn btn-success">PROCESS</button>`;
        amodal.setBodyHtml(html)
        amodal.setTitleText("UPLOAD LOGS")
        amodal.show()
    }
    uploadInCsv(){

        const file = document.getElementById('csv-file').files[0]; // Replace 'csvFileInput' with the actual ID of your file input field

        if (file) {
          const reader = new FileReader();

          reader.onload = function (e) {
              const csvData = e.target.result;
              const rows = csvData.split('\n');
                let recs = 0;
              // Loop through each row starting from the first row
              let date;
              for (let i = 1; i < rows.length; i++) {
                  const rowData = rows[i].split(',');

                  // Now you can access values using array index rowData[index]
                  console.log(rowData);
                  let sec, comp, person, position, phone, email, subject, flag, detail;
                  sec = rowData[0];
                  comp = rowData[1];
                  person = rowData[2];
                  position = rowData[3];
                  phone = rowData[4];
                  email = rowData[5];
                  subject = rowData[6];
                  flag = rowData[7];
                  date = rowData[8]
                  detail = rowData.slice(9).join(', ');
                  console.log(detail)


                  if (rowData.length > 8) {
                      // prepare for api to send
                      recs += 1;
                      let data = {
                          name: person,
                          subject: subject,
                          phone: phone,
                          flag: flag,
                          description: detail,
                          mypk: $('#mypk').val(),
                          company: comp,
                          position: position,
                          email: email,
                          sector: sec, date: date
                      };

                      let payload = {
                          'module': 'log',
                          data: data
                      };

                      console.table(payload);

                      let lg = api.call("PUT", payload, '/crm/api/');
                      console.table(lg)

                  }
              }

              kasa.confirm(`${recs} record(s) loged`,1,'here')
            };

            reader.readAsText(file);
        }


    }

    newSectorScreen() {
        let html = `<input type="text" id="sector" class="form-control rounded-0" />`;
        amodal.setTitleText("Creating Sector");
        amodal.setBodyHtml(html);
        amodal.setFooterHtml(`<button onclick="crm.saveNewSector()" class="btn btn-success">SAVE</button>`)
        amodal.show()
    }

    newPositionScreen() {
        let html = `<input type="text" id="position" class="form-control rounded-0" />`;
        amodal.setTitleText("Creating Position");
        amodal.setBodyHtml(html);
        amodal.setFooterHtml(`<button onclick="crm.saveNewPosition()" class="btn btn-success">SAVE</button>`)
        amodal.show()
    }

    saveNewSector(){
        let fields = ['mypk','sector'];
        if(anton.validateInputs(fields)){
            let payload = {
                module:'sector',
                data:anton.Inputs(fields)
            }
            kasa.confirm(api.call('PUT',payload,'/crm/api/')['message'],0,'here')
            loadSectors()
            amodal.hide()
        } else {
            kasa.error("Invalid Form")
        }


    }

    saveNewPosition(){
        let fields = ['mypk','position'];
        if(anton.validateInputs(fields)){
            let payload = {
                module:'position',
                data:anton.Inputs(fields)
            }
            kasa.confirm(api.call('PUT',payload,'/crm/api/')['message'],0,'here')
            loadPositions()
            amodal.hide()
        } else {
            kasa.error("Invalid Form")
        }


    }

    getSector(s) {
        let payload = {
            module:'sector',
            data:{
                key:s
            }
        }

        return api.call('VIEW',payload,'/crm/api/')
    }

    getPosition(s) {
        let payload = {
            module:'position',
            data:{
                key:s
            }
        }

        return api.call('VIEW',payload,'/crm/api/')
    }

    saveNewLog(){
        let fields = ['sector','company_name','contact_person','position','phone','subject','flag','details','mypk'];
        if(anton.validateInputs(fields)){
            let inputs = anton.Inputs(fields);
            inputs['email'] = $('#email').val()
            let errors = 0;
            let error_message = '';
            // validate dates
            let f_date = $('#follow_up_date').val()


            if(errors === 0){
                let payload = {
                    module:'log',
                    data:inputs
                };
                let save_log = api.call('PUT',payload,'/crm/api/');
                if(anton.IsRequest(save_log)){


                    if(f_date.length > 0){
                        // save follow up
                        let log = save_log['message'];
                        let follow_load = {
                            module:'follow_up',
                            data:{
                                log:log,
                                mypk:$('#mypk').val(),
                                follow_date:$('#follow_up_date').val()
                            }
                        };
                        let save_follow = api.call('PUT',follow_load,'/crm/api/');
                        if(anton.IsRequest(save_follow)){
                            kasa.confirm("Log Saved with follow up and reminder..",1,'here')
                        } else {
                            kasa.response(save_follow);
                        }
                    } else {
                        kasa.confirm("Log Saved..",1,'here')
                    }

                } else {
                    kasa.response(save_log)
                }
            }

        } else {
            kasa.error("Invalid Form")
        }
    }

    PreviewContacts(val) {
        let payload = {
            module:'contacts',
            data:{
                type:val
            }
        };

        let unknown_dom = ``;
        let email_dom = `<table class="table table-responsive datatable">
                <thead>
                    <tr>
                        <th>First Name</th><th>Last Name</th><th>Address</th>
                    </tr>
                </thead>
                <tbody id="emailBody">

                </tbody>
            </table>`;
        let mobile_dom = `<table class="table table-responsive datatable">
                <thead>
                    <tr>
                        <th>First Name</th><th>Last Name</th><th>Mobile</th>
                    </tr>
                </thead>
                <tbody id="emailBody">

                </tbody>
            </table>`;
        let cont = $('#container');
        if(val === 'email'){
            cont.html(email_dom)
        } else if (val === 'mobile'){
            cont.html(mobile_dom)
        } else {
            cont.html(unknown_dom)
        }

        // send payload
        let response = api.call('VIEW',payload,'/crm/api/')
        if(anton.IsRequest(response)){
            console.table(response)
            if(val === 'email' || val === 'mobile'){
                let resp = response['message'];
                let rows = "";
                for(let r = 0; r < resp.length; r++){
                    let row = resp[r];
                    rows += `<tr><td>${row['first_name']}</td><td>${row['last_name']}</td><td>${row['contact']}</td></tr>`
                    console.table(row)
                }

                $('tbody').html(rows)
            }
        } else {
            kasa.response(response)
        }
        console.table(payload)

    }

    previewCampaignEmailTemplate() {
        let temp = $('#email_template');
        amodal.setBodyHtml(temp.val());
        amodal.setTitleText("Campaign Email Template");
        amodal.setSize('L');
        amodal.show();
    }

    saveCampaign() {
        let ids = ['type','title','description','sms_template','email_template','subject','em_sender','sms_api'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:'campaign',
                data:anton.Inputs(ids)
            }

            let sv = api.call('PUT',payload,'/crm/api/');
            if(anton.IsRequest(sv)){
                kasa.confirm(sv['message'],1,'/crm/campaigns/')
            } else {
                kasa.response(sv)
            }

            console.table(payload)
        } else {
            kasa.error("Invalid Form")
        }
    }

    PreviewCampaigns() {
        let camps = this.Campaigns('*');
        if(anton.IsRequest(camps)){
            let cmps = camps['message'];
            let rows = ""
            console.table(camps)
            for(let x = 0; x < cmps.length; x++){
                let row = cmps[x];
                console.table(row)
                rows += `<tr><td>${row['type']}</td><td>${row['title']}</td><td>${row['date']}</td><td>OWNER</td><td>ACTION</td></tr>`
            }
            $('tbody').html(rows);
        } else {
            kasa.response(camps)
        }
    }

    Campaigns(pk) {
        let payload = {
            module:'campaign',
            data:{
                key:pk
            }
        }

        return api.call('VIEW',payload,'/crm/api/')
    }

    extendFollowUpScreen(pk){
        amodal.setTitleText("Extending Follow Up")
        amodal.setBodyHtml(`
            <input type="text" readonly class="form-control rounded-0 mb-2" value="${pk}" id="f_pk">
            <input type="date" class="form-control rounded-0 mb-2" id="date" >
            <textarea name="" id="new_reason" class="form-control rounded-0 mb-2" cols="30" rows="10"></textarea>
        `)
        amodal.setFooterHtml(`<button onclick="crm.extendFollowUp()" class="btn btn-success my-2">Extend</button>`)
        amodal.show()
    }
    extendFollowUp() {
        let ids = ['date','new_reason','f_pk']

        if(anton.validateInputs(ids)){
            let payload = {
                module:'follow_up',
                data:anton.Inputs(ids)
            }


            let patch = api.call('PATCH',payload,'/crm/api/');
            kasa.confirm(patch['message'],1,'here')
        } else {
            kasa.error("Invalid Field")
        }

    }
}

const crm = new Crm()