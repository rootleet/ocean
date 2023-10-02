class Crm {
    newLog(){
        Swal.fire({
          title: 'Enter Data',
          html:
            '<div style="text-align: left !important" class="w-100"><label for="name">COSTOMER NAME</label><input id="name" class="form-control rounded-0 mb-2">' +
            '<label for="subject">SUBJECT</label><input id="subject" class="form-control rounded-0 mb-2">' +
            '<label for="phone">PHONE</label><input type="tel" id="phone" class="form-control rounded-0 mb-2" placeholder="Phone Number">' +
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

            if (
              !name ||
              !subject ||
              !phone ||
              flag === '' ||
              !description
            ) {
              Swal.showValidationMessage('Please fill in all fields');
            }

            // Return an object with the values of the input fields
            let x = {
              name: name,
              subject: subject,
              phone: phone,
              flag: flag,
              description: description,
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
                mypk:$('#mypk').val()
            };

            let payload = {
                'module':'log',
                data:data
            };

            console.table(payload);

            let lg = api.call("PUT",payload,'/crm/api/');
            kasa.info(lg['message'])

          }
        });

    }
}

const crm = new Crm()