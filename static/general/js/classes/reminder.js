class Reminder {
    newReminder(){
        Swal.fire({
          title: 'SET REMINDER',
          html: `
            <input id="swal-date" type="date" class="form-control rounded-0 mb-2">
            <input id="swal-time" type="time" class="form-control rounded-0 mb-2">
            <input id="swal-title" class="form-control rounded-0 mb-2" placeholder="Title">
            <textarea id="swal-message" class="form-control rounded-0 mb-2" placeholder="Message" cols="30" rows="5"></textarea>
            
          `,

          focusConfirm: false,
          confirmButtonText: 'Submit',
            showCancelButton: true,
            cancelButtonText:'CANCEL',
            confirmButtonColor:'#19541b',
          preConfirm: () => {
            const title = document.getElementById('swal-title').value
            const message = document.getElementById('swal-message').value
            const date = document.getElementById('swal-date').value
            const time = document.getElementById('swal-time').value

            if (!title || !message || !date || !time) {
              Swal.showValidationMessage(`Please fill all fields`)
            }

            return {title: title, message: message, date: date, time: time}
          },
        }).then((result) => {
          if (result.isConfirmed) {
              let data = result.value
              data['owner'] = $('#mypk').val()
              let payload = {
                  'module':'reminder',
                  data:data
              };
              let response = api.call('PUT',payload,'/adapi/')
              kasa.info(response['message'])
              console.table(payload)
            console.log(result.value)
          }
        })
    }

    editReminder(key){
        let payload = {
            'module':'reminder',
            'data':{
                owner:$('#mypk').val(),
                key:key,
            }
        }
        let response = api.call('VIEW',payload,'/adapi/')

        if(response['status_code'] === 200){
            let reminder = response['message'][0]

            Swal.fire({
          title: 'EDIT REMINDER',
          html: `
            <input id="swal-date" value="${reminder['date']}" type="date" class="form-control rounded-0 mb-2">
            <input id="swal-time" value="${reminder['time']}" type="time" class="form-control rounded-0 mb-2">
            <input id="swal-title" value="${reminder['title']}" class="form-control rounded-0 mb-2" placeholder="Title">
            <textarea id="swal-message"  class="form-control rounded-0 mb-2" placeholder="Message" cols="30" rows="5">${reminder['message']}</textarea>
            
          `,

          focusConfirm: false,
          confirmButtonText: 'Submit',
            showCancelButton: true,
            cancelButtonText:'CANCEL',
            confirmButtonColor:'#19541b',
          preConfirm: () => {
            const title = document.getElementById('swal-title').value
            const message = document.getElementById('swal-message').value
            const date = document.getElementById('swal-date').value
            const time = document.getElementById('swal-time').value

            if (!title || !message || !date || !time) {
              Swal.showValidationMessage(`Please fill all fields`)
            }

            return {title: title, message: message, date: date, time: time}
          },
        }).then((result) => {
              if (result.isConfirmed) {
                  let data = result.value
                  data['pk'] = key
                  data['task'] = 'all'
                  let payload = {
                      'module':'reminder',
                      data:data
                  };
                  let response = api.call('PATCH',payload,'/adapi/')
                  kasa.info(response['message'])
                  load_my_reminder()

              }
            })

        } else {
            kasa.html(`THERE IS AN ERROR GETTING TASK <br> <i class="text-danger">${response['message']}</i>`)
        }

    }

    switchReminder(status,key){
        let payload = {
            'module':'reminder',
            data:{
                'task':'status',
                'status':status,
                pk:key
            }
        }



        let response = api.call('PATCH',payload,'/adapi/')
        return response['message']

    }

    enable(key){
        kasa.info(reminder.switchReminder('enable',key))
        load_my_reminder()
    }
    disable(key){

        kasa.info(reminder.switchReminder('disable',key))
        load_my_reminder()
    }

}

const reminder = new Reminder()