class Crm {
    newLog(){
        Swal.fire({
          html:
            '<div style="text-align: left !important" class="w-100">' +
              '<label for="sector">SECTOR</label>' +
              '<select id="sector" class="form-control mb-2 rounded-0">' +
              '<option value="Accounting">Accounting</option>\n' +
              '  <option value="Agriculture">Agriculture</option>\n' +
              '  <option value="Arts">Arts</option>\n' +
              '  <option value="Construction">Construction</option>\n' +
              '  <option value="Education">Education</option>\n' +
              '  <option value="Engineering">Engineering</option>\n' +
              '  <option value="Finance">Finance</option>\n' +
              '  <option value="Healthcare">Healthcare</option>\n' +
              '  <option value="Information Technology">Information Technology</option>\n' +
              '  <option value="Legal">Legal</option>\n' +
              '  <option value="Manufacturing">Manufacturing</option>\n' +
              '  <option value="Marketing">Marketing</option>\n' +
              '  <option value="Media">Media</option>\n' +
              '  <option value="Non-profit">Non-profit</option>\n' +
              '  <option value="Retail">Retail</option>\n' +
              '  <option value="Sales">Sales</option>\n' +
              '  <option value="Science">Science</option>\n' +
              '  <option value="Social Services">Social Services</option>\n' +
              '  <option value="Transportation">Transportation</option>' +
              '</select>' +
              '<label for="company">COMPANY NAME</label><input id="company" class="mb-2 form-control rounded-0"> <hr>' +
              '<label for="name">CONTACT PERSON</label><input id="name" class="form-control rounded-0 mb-2">' +
              '<label for="position">POSITION</label><select name="" id="position" class="form-control rounded-0 mb-2">' +
              '<option value="CEO">CEO</option>\n' +
              '  <option value="COO">COO (Chief Operating Officer)</option>\n' +
              '  <option value="CFO">CFO (Chief Financial Officer)</option>\n' +
              '  <option value="HR Manager">HR Manager</option>\n' +
              '  <option value="Operations Manager">Operations Manager</option>' +
              '<option value="Tranport Manager">Transport Manager</option>' +
              '<option value="Receptionist">Receptionist</option>' +
              '<option value="Others">Others</option>' +
              '</select>' +
            '<label for="phone">PHONE</label><input type="tel" id="phone" class="form-control rounded-0 mb-2" placeholder="Phone Number">' +
              '<label for="email">EMAIL ADDRESS</label><input id="email" type="email" class="form-control rounded-0 mb-2"><hr>' +
              '<label for="subject">SUBJECT</label><input id="subject" class="form-control rounded-0 mb-2">' +
            '<label for="flag">FLAG</label><select id="flag" class="form-control rounded-0 mb-2">' +
            '<option value="" disabled selected>Select an option</option>' +
            '<option value="success">SUCCESS</option>' +
            '<option value="uncreachable">UNREACHABLE</option>' +
            '</select>' +
            '<label for="description">DETAILS</label><textarea id="description" rows="5" class="form-control rounded-0 mb-2" placeholder="Details"></textarea></div>',
          focusConfirm: false,
          showCancelButton: true,
          confirmButtonText: 'Save',
          cancelButtonText: 'Cancel',
          preConfirm: () => {
            const name = document.getElementById('name').value;
            const subject = document.getElementById('subject').value;
            const flag = document.getElementById('flag').value;
            const phone = document.getElementById('phone').value;
            const description = document.getElementById('description').value;
            let sector = document.getElementById('sector').value;
            let email = document.getElementById('email').value;
            let position = document.getElementById('position').value;
            let company = document.getElementById('company').value;

            if (
              !name ||
              !subject ||
              !phone ||
              flag === '' ||
              !description || !sector || !email || !position || !company
            ) {
              Swal.showValidationMessage('Please fill in all fields');
            }

            // Return an object with the values of the input fields
            let x = {
              name: name,
              subject: subject,
              phone: phone,
              flag: flag,
              description: description,sector:sector,email:email,position:position,company:company
            };

            return x;

          },
        }).then((result) => {
          if (result.isConfirmed) {
            let vals = result.value
            let data = {
                name:vals.name,
                subject:vals.subject,
                phone:vals.phone,
                flag:vals.flag,
                description:vals.description,
                mypk:$('#mypk').val(),
                company:vals.company,
                position:vals.position,
                email:vals.email,
                sector:vals.sector
            };

            let payload = {
                'module':'log',
                data:data
            };

            console.table(payload);

            let lg = api.call("PUT",payload,'/crm/api/');
            location.reload()
            kasa.info(lg['message'])

          }
        });

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
}

const crm = new Crm()