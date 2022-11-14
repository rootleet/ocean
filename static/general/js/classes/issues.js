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
}

const issues = new Issues();