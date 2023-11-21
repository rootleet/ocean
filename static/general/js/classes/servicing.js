class Servicing{
    newServiceType(){

        amodal.show()
        
    }

    newSub(){
        amodal.setTitleText('Creating Service Sub');
        amodal.setBodyHtml(`<input class="form-control rounded-0 mb-2" placeholder="Name" id="sub_name"><textarea class="form-control rounded-0" placeholder="Description" id="description" rows="3"></textarea>`);
        amodal.setFooterHtml(`<button onclick="servicing.saveNewSub()" class="btn btn-success w-100">SAVE</button>`)
        amodal.show();
    }

    saveNewSub() {
        let ids = ['sub_name','service_code','description']
        if(anton.validateInputs(ids)){
            let data = anton.Inputs(ids);
            data['owner_id'] = $('#mypk').val();
            let payload = {
                'module':'service_sub',
                data:data
            }

            let response = api.call('PUT',payload,'/servicing/api/');
            kasa.confirm(response['message'],1,'here')

        } else {
            kasa.error("Fill All Required Fields")
        }
    }

    newTechnician() {
        let users = user.allUsers();

        if(users['status_code'] === 200){
            let options = '';
            let all_users = users['message'];
            for (let u = 0; u < all_users.length; u++) {
                let user = all_users[u];
                options += `<option value="${user['pk']}">${user['fullname']}</option>`;
            }
            amodal.setTitleText('Add Technician');
            amodal.setBodyHtml(`<select class="form-control rounded-0" id="technician">${options}</select>`);
            amodal.setFooterHtml(`<button onclick="servicing.saveTechnician()" class="btn btn-success w-100">SAVE</button>`)
            amodal.show();
        } else {
            kasa.error(users['message']);
        }
    }

    saveTechnician() {
        let ids = ['technician','service_code'];
        if(anton.validateInputs(ids)){
            let payload = {
                'module':'service_technician',
                data:anton.Inputs(ids)
            };
            kasa.confirm(
                api.call('PUT',payload,'/servicing/api/')['message'],1,'here'
            )
        } else {
            kasa.error("Fill Required Fields")
        }
    }
}

const servicing = new Servicing()