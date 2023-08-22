class Forms {
    // get html

    saveNew() {
        let frame =  ace.edit("editor");
        let html = frame.getValue();

        if(html.length > 0){
            amodal.hide()
            Swal.fire({
              title: 'SAVE NEW FORM',
              input: 'text',
              inputAttributes: {
                autocapitalize: 'on',
                  placeholder:"form unique name"
              },
              showCancelButton: true,
              confirmButtonText: 'Submit',
              cancelButtonText: 'Cancel',
              showLoaderOnConfirm: true,
              preConfirm: (input) => {
                if (!input) {
                  Swal.showValidationMessage('Input cannot be empty');
                }
                return input;
              },
              allowOutsideClick: () => !Swal.isLoading()
            }).then((result) => {
              if (result.isConfirmed) {
                const inputValue = result.value;
                let frame =  ace.edit("editor");
                let html = frame.getValue();

                 let data = {
                     'doc':'SAVE_FORM',
                     'output':html,
                     'key':inputValue,

                 }
                 let payload = {
                     'module':'not-set',
                     data:data
                 }

                 let response = api.call('PUT',payload,'/reports/api/');

                 if(response['status_code'] === 200){
                     kasa.confirm(response['message'],1,'/reports/')
                 } else {
                     kasa.error(response['message'])
                 }

              }
            });

        } else {
            kasa.error("CANNOT SAVE EMPTY FORM")
        }



    }

    newReportLegend(){
        Swal.fire({
          title: 'LEGEND DETAILS',
          html:
            '<input id="swal-input1" class="form-control w-100 mb-2" placeholder="Legend...">' +
            '<textarea id="swal-input2" class="form-control w-100" rows="5" placeholder="Description..."></textarea>',
          showCancelButton: true,
          confirmButtonText: 'Submit',
          cancelButtonText: 'Cancel',
          showLoaderOnConfirm: true,
          preConfirm: () => {
            const input1 = document.getElementById('swal-input1').value;
            const input2 = document.getElementById('swal-input2').value;

            if (!input1 && !input2) {
              Swal.showValidationMessage('At least one input should not be empty');
            }

            return [input1, input2];
          },
          allowOutsideClick: () => !Swal.isLoading()
        }).then((result) => {
          if (result.isConfirmed) {
            const [inputValue1, inputValue2] = result.value;

            let data = {
                     'doc':'SAVE_REPORT_LEGEND',
                     'output':inputValue2,
                     'key':inputValue1,

            }
            let payload = {
                     'module':'not-set',
                     data:data
            }

            let response = api.call('PUT',payload,'/reports/api/');

            if(response['status_code'] === 200){
                     kasa.confirm(response['message'],1,'/reports/')
            } else {
                     kasa.error(response['message'])
            }

          }
        });

    }

    newReportLegendSub(legend){
        Swal.fire({
          title: 'LEGEND DETAILS',
          html:
            '<input id="swal-input3" class="form-control w-100 mb-2" placeholder="name...">' +
              '<input id="swal-input1" class="form-control w-100 mb-2" placeholder="action...">' +
            '<textarea id="swal-input2" class="form-control w-100" rows="5" placeholder="Description..."></textarea>',
          showCancelButton: true,
          confirmButtonText: 'Submit',
          cancelButtonText: 'Cancel',
          showLoaderOnConfirm: true,
          preConfirm: () => {
            const input1 = document.getElementById('swal-input1').value;
            const input2 = document.getElementById('swal-input2').value;
             const input3 = document.getElementById('swal-input3').value;

            if (!input1 && !input2 && !input3) {
              Swal.showValidationMessage('At least one input should not be empty');
            }

            return [input1, input2, input3];
          },
          allowOutsideClick: () => !Swal.isLoading()
        }).then((result) => {
          if (result.isConfirmed) {
            const [inputValue1, inputValue2,name] = result.value;

            let data = {
                'doc':'SAVE_REPORT_LEGEND_SUB',
                'description':inputValue2,
                'action':inputValue1,
                'legend':legend,
                'name':name

            }
            let payload = {
                     'module':'not-set',
                     data:data
            }

            let response = api.call('PUT',payload,'/reports/api/');

            if(response['status_code'] === 200){
                     kasa.confirm(response['message'],1,'/reports/')
            } else {
                     kasa.error(response['message'])
            }

          }
        });

    }
}

const phorm = new Forms()