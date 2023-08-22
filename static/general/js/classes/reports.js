class Reports {

    cmms_sales_customer(){
        let table_header = ['TYPE OF','NAME','COMPANY','ADDRESS','PHONE','EMAIL','REGION','SUBURB','DATE','OWNER']
        // get customers
        let response = cmms_sales.getCustomer()
        let rows = ''
        if(response['status_code'] === 200){
            // if there are customers
            let customers = response['message'];
            console.table(customers)
            for (let cust = 0; cust < customers.length; customers++) {
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