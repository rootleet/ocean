class Issues {
    // new branch
    async createBranch() {


        const { value: br_name } = await Swal.fire({
          title: 'Creating A Branch',
          input: 'text',
          inputLabel: 'Branch Name',
          showCancelButton: true,
          inputValidator: (value) => {
            if (!value) {
              return 'You need to write something!'
            }
          }
        })

        if (br_name) {


            const { value: text } = await Swal.fire({
              input: 'textarea',
              inputLabel: 'Description',
              inputPlaceholder: 'Describe Your Branch...',
              inputAttributes: {
                'aria-label': 'Type your message here'
              },
              showCancelButton: true
            })

            if (text) {
              let data = {'branch_name':br_name,'parent_task':$('#task').val(),'description':text}
                let apicall = api_call('issues','newBranch',data)
                let r = JSON.parse(apicall)
                if(r['status'] == 200)
                {
                    location.reload()
                } else {
                    swal_success(r['staus'])
                }
                // Swal.fire(`API RESPONSE : ${apicall['message']}`)
            }




        }
    }

    async updateBranch() {
        const {value: text} = await Swal.fire({
            input: 'textarea',
            inputLabel: 'UPDATE',
            inputPlaceholder: 'Update...',
            inputAttributes: {
                'aria-label': 'Type your message here'
            },
            showCancelButton: true
        })

        if (text) {
            let branchId = $('#branchId').val()
            let apcall = api_call('issues','updateBranch',{'descr':text,'br':branchId})
            let r = JSON.parse(apcall)
            if(r['status'] === 200)
            {
                location.reload()
            } else {
                error_handler('error%%Count Not Save Update')
            }

        }
    }



    Export(){
        let d_opt = ''
        let domains = api.view({"module":"domain"})['message']

        for (let d = 0; d < domains.length ; d++) {
            let op = domains[d]
            d_opt += `<option value="${op['pk']}">${op['desc']}</option>`
        }
        Swal.fire({
            title: 'Export Data',
            html:
              '<form style="text-align: left !important">' +
              '<div class="form-group mb-3">' +
              '<label for="doc_type">Document Type</label>' +
              '<select id="doc_type" class="form-control">' +
              '<option value="" selected disabled>Select Document</option>' +
              '<option value="excel">Excel</option>' +
              '<option value="json" disabled>JSON</option>' +
              '</select>' +
              '</div>' +
              '<div class="form-group mb-3">' +
              '<label for="domain">Domain</label>' +
              '<select id="domain" class="form-control">' +
              '<option value="" selected disabled>Select Domain</option>' +
              d_opt +
              '</select>' +
              '</div>' +
              '<div class="form-group ">' +
              '<label for="status">Status</label>' +
              '<select id="status" class="form-control">' +
              '<option value="" selected disabled>Select Status</option>' +
              '<option value="1">Close</option>' +
              '<option value="0">Open</option>' +
              '<option value="*">All</option>' +
              '</select>' +
              '</div>' +
              '</form>',
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Export',
            cancelButtonText: 'Close',
            preConfirm: function() {
              var docType = $('#doc_type').val();
              var domain = $('#domain').val();
              var status = $('#status').val();

              if (!docType || !domain || !status) {
                Swal.showValidationMessage('Please select an option for all fields');
                return false;
              }

              return { docType: docType, domain: domain, status: status };
            }
          }).then(function(result) {
            if (result.isConfirmed) {
              var docType = result.value.docType;
              var domain = result.value.domain;
              var status = result.value.status;
              console.log('Doc Type:', docType);
              console.log('Domain:', domain);
              console.log('Status:', status);

              let data = {
                  'module':'taskmanager',
                  'data':{
                      'format':docType,'domain':domain,'status':status
                  }
              }

              console.table(data)

              let view = api.view(data)
                console.table(view)
                if(view['status_code'] === 200){
                    Swal.fire({
                        'icon':'success',
                        'text':"Download file with the link below",
                        'html':`Download file with the link below <br><a href="/${view['message']}" target="_blank">LINK</a>`
                    })
                } else {
                    Swal.fire({
                        'icon':'info',
                        'title':view['status_code'],
                        'text':view['message'],
                    })
                }
            }
          });
    }

}

const issues = new Issues();