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

    changeLocationManager(loc_pk) {

        try {
             // get users
            let users = this.allUsers(true);

            if(anton.IsRequest(users)){
                let ops = `<option value="">SELECT MANAGER</option>`
                let msg = users.message
                for (let i = 0; i < msg.length; i++) {
                    let us = msg[i]
                    ops += `<option value="${us['pk']}">${us['fullname']}</option>`
                }
                let form = ``
                form += fom.select('manager',ops,'',true)
                form += `<input id="loc_pk" type="hidden" value="${loc_pk}">`
                amodal.setTitleText(`Set Location Manager`)
                amodal.setBodyHtml(form)
                amodal.setFooterHtml(`<button onclick="user.setLocationManager()" class="btn btn-success w-100">SET</button>`)
                amodal.show()
            } else {
                throw(`Error getting users ${users.message}`)
            }
        } catch (e) {
            kasa.error(e)
        }

    }

    allUsers(users_with_adon=false){
        let m = 'users';
        if(users_with_adon){
            m = 'users_with_adon'
        }
        let payload = {
            module:m
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

    makeApprovalScreen(pk){
        let permissions = {
            'sales_proforma':"CMMS SALES PROFORMA"
        }

        let options = `<option value=''>Select Document</option>`
        for (const key in permissions) {
            if (Object.hasOwnProperty.call(permissions, key)) {
                const element = permissions[key];
                options += `<option value='${key}'>${element}</option>`
            }
        }

        // make form
        let form  = "";
        form += fom.select('doc_type',options,'',true)
        form += `<input type='hidden' id='user_pk' value='${pk}' >`

        amodal.setBodyHtml(form)
        amodal.setFooterHtml(`<button onclick='user.saveApproval()' class='btn btn-success w-100'>PERMIT</button>`)
        amodal.show()
    }

    saveApproval(){
        let fields = ['doc_type','user_pk','loc_pk'];
        if(anton.validateInputs(fields)){
            let payload = {
                module:'doc_app_auth',
                data:anton.Inputs(fields)
            }
            amodal.hide()
            kasa.response(api.call('PUT',payload,'/adapi/'))
        } else {
            kasa.error("Invalid Form Field")
        }
    }

    setLocationManager() {
        let fields = ['manager','mypk','loc_pk'];
        try {
            if(anton.validateInputs(fields)){

                let payload = {
                    module:'set_loc_manager',
                    data:anton.Inputs(fields)
                }

                let swi = api.call('PUT',payload,'/adapi/')
                console.table(swi)
                if(anton.IsRequest(swi)){
                    kasa.confirm(swi.message,1,'here')
                } else {
                    throw (`${swi.message}`)
                }

                console.table(payload)
                amodal.hide()
            } else {
                throw ("Invalid Forms")
            }
        } catch (e){
            kasa.error(e)
        }
    }
}

const user = new User()

