class User {

    Delete(pk) {
        if(confirm("ARE YOU SURE"))
        {
            let apireturn = api_call('user','delete',{'user':pk})
            let r = JSON.parse(apireturn)

            if(r['status'] === 200)
            {
                swal_reload("User Deleted")
            } else
            {
                error_handler(r['message'])
            }
        }

    }

    allUsers(){
        let payload = {
            module:'users'
        };

        return api.call('VIEW', payload, '/adapi/');
    }

    resetPassword(key) {
        let payload = {
            'module':'rest_password',
            data:{
                user:key
            }
        }

        console.table(payload)

        let response = api.call('PATCH',payload,'/adapi/');
        kasa.confirm(response['message'],1,'here');
    }

    resetAllPasswords() {
        Swal.fire({
          title: 'Are you sure?',
          text: 'You won\'t be able to revert this!',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Yes, execute!',
          cancelButtonText: 'Cancel'
        }).then((result) => {
          if (result.isConfirmed) {
            // Code to execute when confirmed
            let payload = {
                module:'all_password_reset',
                data: {

                }
            };
            let request = api.call('PATCH',payload,'/adapi/');
            kasa.confirm(request['message'],1,'here')
            // Add your code to execute here
          } else {
            // Code to execute when not confirmed (or canceled)
            Swal.fire(
              'Cancelled',
              'Your operation has been cancelled.',
              'info'
            );
            // Add your code for when the user cancels here
          }
        });

    }
}

const user = new User()