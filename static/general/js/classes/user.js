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
}

const user = new User()