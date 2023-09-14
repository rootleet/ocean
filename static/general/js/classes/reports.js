class Reports {

    cmms_sales_customer(){
        let table_header = ['TYPE OF','NAME','COMPANY','ADDRESS','PHONE','EMAIL','REGION','SUBURB','DATE','OWNER']
        // get customers
        let response = cmms_sales.getCustomer('all')
        let rows = ''
        if(response['status_code'] === 200){
            // if there are customers
            let customers = response['message'];
            console.table(customers)
            for (let cust = 0; cust < customers.length; cust++) {
                let customer = customers[cust]
                rows += `
                    <tr>
                        <td><a onclick="windowPopUp('/cmms/sales/deals/${customer['url']}/','CUSTOMER SCREEN',1000,600)" href="javascript:void(0)">${customer['type_of_client']}</a></td>
                        <td>${customer['name']}</td>
                        <td>${customer['company']}</td>
                        <td>${customer['address']}</td>
                        <td>${customer['mobile']}</td>
                        <td>${customer['email']}</td>
                        <td>${customer['geography']['region']}</td>
                        <td>${customer['geography']['suburb']}</td>
                        <td>${customer['timestamp']['created_date']} ${customer['timestamp']['created_time']}</td>
                        <td>${customer['owner']['username']}</td>
                    </tr>
                `
            }

        } else {
            rows = response['message']
        }

        reports.render(table_header,rows,"CMMS SALE CUSTOMERS")
    }

    cmms_sales_deals(){
        let customer = $('#customerSelect');
        let deals = cmms_sales.getDeals(customer);
        console.table(deals)
    }

    all_tasks(){
        let userss = anton.Users()['message'];
        let us = ''
        for (let u = 0; u < userss.length ; u++) {
            let user = userss[u]
            us += `<option value="${user['pk']}">${user['name']}</option>`
        }
        let form = `
            <div class="w-100 container" style="text-align: left">
                <div class="row mb-2"><hr>
                    <div class="col-sm-6"><label for="from"><strong class="text-info">FROM</strong></label><input type="date" id="from" class="form-control" /></div>
                    <div class="col-sm-6"><label for="to"><strong class="text-info">TO</strong></label><input type="date" id="to" class="form-control" /></div>
                </div>
                
                <div class="row mb-2">
                    <div class="col-sm-6">
                        <label for="status"><strong class="text-info">STATUS</strong></label>
                        <select name="" id="status" class="form-control">
                            <option value="*">ALL</option>
                            <option value="1">OPEN</option>
                            <option value="2">CLOSED</option>
                        </select>
                    </div>
                    <div class="col-sm-6">
                        <label for="user"><strong class="text-info">USER</strong></label>
                        <select name="" id="user" class="form-control">
                            ${us}
                        </select>
                    </div>
                </div>
            </div>
            
        `;
        Swal.fire({
        title: 'TASKS FILTER OPTION',
        html: form,
        showCancelButton: true,
        confirmButtonText: 'SUBMIT',
        cancelButtonText: 'Cancel',
        reverseButtons: true, // To swap the positions of "Cancel" and "OK" buttons
      }).then((result) => {

        if (result.isConfirmed) {
            const status = $('#status').val();
            const from = $('#from').val();
            const to = $('#to').val();
            const  user = $('#user').val()

            // validate inputs
            if(anton.validateInputs(['status','from','to'])){
                // validate date range
                // if(from < to){
                //     kasa.error("From date cannot be lesser than to date")
                // } else {
                //     kasa.success("LETS GOO")
                // }

                let payload = {
                    module:'all',
                    data: {
                        from:from,
                        to:to,
                        status:status,
                        user:user
                    }
                }

                // send payload
                let response = api.call('VIEW',payload,'/taskmanager/api/')
                if(response['status_code'] === 200){
                    let message = response['message'];
                    let row = '';
                    for (let tk = 0; tk < message.length ; tk++) {
                        let task = message[tk]
                        row += `
                            <tr><td>${task['owner']}</td><td>${task['date']}</td><td>${task['title']}</td><td><a onclick="windowPopUp('/taskmanager/view/${task['uni']}/','',1024,632)" href="javascript:void(0)">${task['task_inline']}</a></td></tr>
                        `;

                    }
                     reports.render(['OWNER','DATE','TITLE','INLINE'],row)
                } else {
                    kasa.error(response['message'])
                }



            } else {
                kasa.error("FILL ALL FIELDS")
            }


        } else {
          Swal.fire('Cancelled', 'You cancelled the action', 'error');
        }
      });
    }

    render(header = [],rows = '',report_title = ''){
        if(header.length < 1){
            kasa.error("INVALID HEADER LENDER : REPORT CANNOT RENDER")
        } else {
            let th = ''
            for (let h = 0; h < header.length; h++){
                th += `<th>${header[h]}</th>`
            }

            let table = `<table class="table table-sm table-bordered"><thead><tr>${th}</tr></thead><tbody>${rows}</tbody></table>`
            let menu = card.getBody()
            card.setTitle(report_title)
            card.setBody(table)
            card.setFooter(`<button class="btn btn-success" onclick="">HOME</button>`)

        }
    }
}

const reports = new Reports()