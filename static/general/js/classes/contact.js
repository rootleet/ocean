class Contact {
    create(){
        Swal.fire({
          title: 'NEW CONTACT',
          html: `
            <input id="cont_full_name" placeholder="Full Name" type="text" class="form-control rounded-0 mb-2">
            <input id="cont_phone" placeholder="Phone" type="tel" class="form-control rounded-0 mb-2">
            <input id="cont_email" placeholder="Email" type="email" class="form-control rounded-0 mb-2">
          `,

          focusConfirm: false,
          confirmButtonText: 'Submit',
            showCancelButton: true,
            cancelButtonText:'CANCEL',
            confirmButtonColor:'#19541b',
          preConfirm: () => {
            const full_name = document.getElementById('cont_full_name').value
            const phone = document.getElementById('cont_phone').value
            const email = document.getElementById('cont_email').value

            if (!full_name || !phone || !email) {
              Swal.showValidationMessage(`Please fill all fields`)
            }

            return {full_name: full_name, phone: phone, email: email}
          },
        }).then((result) => {
          if (result.isConfirmed) {
              let data = result.value
              data['owner'] = $('#mypk').val()
              let payload = {
                  'module':'reminder',
                  data:data
              };

              kasa.info(api.call('PUT',payload,'/apiv2/contact/')['message'])
              console.table(payload)
          }
        })
    }
}

const contact = new Contact()