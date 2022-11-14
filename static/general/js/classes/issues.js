class Issues {
    // new branch
    async createBranch() {


        const { value: text } = await Swal.fire({
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

        if (text) {
            let data = {'br_name':text,'task':$('#task').val()}
            let apicall = api_call('issues','newBranch',data)

          Swal.fire(`Your IP address is ${apicall}`)
        }
    }
}

const issues = new Issues();