class Maintenance {
    constructor() {
        this.api_interface = '/maintainance/api/'
    }
    newScreen(){
        let form = "";
        form += fom.text('title','',true);
        form += fom.textarea('description',10,true)


        amodal.setBodyHtml(form);
        amodal.setTitleText("ADDING NEW MAINTAINED SERVICE");
        amodal.setFooterHtml(`<button onclick="maintenance.saveNew()" class="btn btn-success w-100">SAVE</button>`)
        amodal.show()
    }

    saveNew() {
        let ids = ['title','description','mypk'];
        if(anton.validateInputs(ids)){
            api.payload['module'] = 'maintenance_request';
            api.payload['data'] = anton.Inputs(ids);

            let response = api.call('PUT',api.payload,'/maintainance/api/');
            kasa.response(response)
        } else {
            kasa.error("Fill All Fields")
        }
    }

    update_maintenance(){

        let form = "";

        form += fom.text('title','',true);
        form += fom.textarea('description',4,true);

        amodal.setBodyHtml(form);
        amodal.setTitleText("UPDATE RECORDS");
        amodal.setFooterHtml(`<button onclick="maintenance.updateRecord()" class="btn btn-success w-100">SAVE</button>`);
        amodal.show()
    }

    updateRecord() {
        let ids = ['maintenance','mypk','title','description'];
        if(anton.validateInputs(ids)){
            api.payload['module'] = 'maintenance_log';
            api.payload['data'] = anton.Inputs(ids);

            let response = api.call('PUT',api.payload,'/maintainance/api/');
            kasa.confirm(response['message'],1,'here');

        } else {
            kasa.error("Fill All Fields");
        }
    }

    close_screen() {

        Swal.fire({
          title: 'Are you sure?',
          text: 'You won\'t be able to revert this!',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Yes, proceed!',
          cancelButtonText: 'Cancel'
        }).then((result) => {
          // Check if the user clicked the confirm (yes) button
          if (result.isConfirmed) {

              let form = '';
              form += fom.textarea('message',5,true)
              amodal.setTitleText("CLOSING MESSAGE")
              amodal.setBodyHtml(form);
              amodal.setFooterHtml(`<button onclick="maintenance.close()" class="btn btn-success w-100">CLOSE</button>`);
              amodal.show()

          }
        });

    }

    close() {
        let ids = ['mypk','maintenance','message'];
        if(anton.validateInputs(ids)){
            api.payload['data'] = anton.Inputs(ids);
            api.payload['module'] = 'close';

            let response = api.call('PATCH',api.payload,'/maintainance/api/');
            kasa.confirm(response['message'],1,'here');

        } else {
            kasa.error("Fill Required Fields")
        }
    }

    getGroup(key='*'){
        let payload = {
            module:'maintenance_asset_group',
            data:{
                key:key
            }
        }
        return api.call('VIEW',payload,this.api_interface);


    }

    new_asset_group_screen() {
        let form = '';
        form += fom.text('name','Group Name',true);
        amodal.setTitleText("New Maintainance Asset");
        amodal.setBodyHtml(form);
        amodal.setFooterHtml(`<button onclick="maintenance.save_asset_group()" class="btn btn-success">SAVE</button>`);
        amodal.show();

    }

    save_asset_group() {
        let ids = ['mypk','name'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:'maintenance_asset_group',
                data:anton.Inputs(ids)
            }
            kasa.confirm(
                api.call('PUT',payload,this.api_interface)['message'],1,'here'
            )
        } else {
            kasa.error("Fill All Fields")
        }
    }
}

const maintenance = new Maintenance()