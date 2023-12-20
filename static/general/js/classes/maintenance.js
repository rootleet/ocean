class Maintenance {
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
}

const maintenance = new Maintenance()