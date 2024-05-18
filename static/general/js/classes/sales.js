class Sales {
    salesSummary(day=today)
    {
        $('#g_modal_title').text('SALES SUMMARY')
        let sales_summary = JSON.parse(apiv2('sales','summary',{'day':day}))
        ctable(sales_summary)

        let status,message,html
        status = sales_summary['status']
        message = sales_summary['message']

        if(status === 404)
        {
            // nothing to show
            html = `<div class="alert text-center alert-info"><strong>NO SALES YET</strong><br><small class="text-danger">Contact System Administrator if otherwise</small></div>`

        } else {
            html = `<table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Gross</th>
                                            <th>Discount</th>
                                            <th>Tax</th>
                                            <th>Net</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>${message['gross_sales']}</td>
                                            <td>${message['discount']}</td>
                                            <td>${message['tax']}</td>
                                            <td>${message['net_sales']}</td>
                                        </tr>
                                    </tbody>
                                </table>`
        }
        $('#g_modal_body').html(html)
        $('#g_modal').modal('show')


    }

    detailSales(day=today) {
        $('#g_modal_title').text('DETAIL SALES')
        console.log(day)
        let sales_summary = JSON.parse(apiv2('sales','loc_wise',{'day':day}))


        let status,message,html
        status = sales_summary['status']
        message = sales_summary['message']

        if(status === 404)
        {
            // nothing to show
            html = `<div class="alert text-center alert-info"><strong>NO SALES YET</strong><br><small class="text-danger">Contact System Administrator if otherwise</small></div>`

        } else {
                ctable(message)
            let tr = ""
            for (let i = 0; i < message.length; i++) {
                let t_m = message[i]
                let loc,mech_no,gross_sales,discount,tax,net_sales
                loc = t_m.loc
                mech_no = t_m.mech_no
                gross_sales = t_m.gross_sales
                discount = t_m.discount
                tax = t_m.tax
                net_sales = t_m.net_sales

                tr += `<tr>
                    <td>${loc}</td>
                    <td>${mech_no}</td>
                    <td>${gross_sales}</td>
                    <td>${discount}</td>
                    <td>${tax}</td>
                    <td>${net_sales}</td>
                </tr>`



            }
            html = `<div class="card"> <div class="card-body p-2"><table class="table table-responsive table-bordered">
                        <thead>
                            <tr>
                                <th>LOCATION</th><th>MACHINE</th><th>GROSS</th><th>DISCOUNT</th><th>TAX</th><th>NET</th>
                            </tr>
                        </thead>
                        <tbody>
                           ${tr}
                        </tbody>
                    </table></div></div>`
        }
        $('#g_modal_body').html(html)
        $('#g_modal_size').addClass('modal-lg')
        $('#g_modal').modal('show')
    }

    total(day=today){
        let sales_summary = JSON.parse(apiv2('sales','today',{'day':day}));
        console.table(sales_summary)
        $("#total").text(sales_summary.message)
    }

    viewAssetGroups(){
        let assets = this.getAssetGroup('*');
        if(anton.IsRequest(assets)){
            let tr = ``;
            let groups = assets['message'];
            for(let g= 0; g < groups.length; g++){
                let group = groups[g]
                tr += `<tr><td>${group['name']}</td><th>void</th></tr>`;
            }
            let table = `
                <button class="tn btn-sm btn-info" onclick="sales.newAssetGroup()">NEW</button>
                <table class="table table-sm table-striped">
                    <thead><tr><th>Name</th><th>Action</th></tr></thead>
                    <tbody>${tr}</tbody>
                </table>
            `;
            amodal.setBodyHtml(table);
        } else {
            amodal.setBodyHtml(`<div class="alert alert-danger">${assets['message']}</div>`)
        }
        console.table(assets)
        amodal.setTitleText("ASSET GROUPS")

        amodal.show()
    }

    newAssetGroup() {
        let form = fom.text('g_name','',true);
        amodal.setTitleText('Creating New Asset Group')
        amodal.setBodyHtml(form);
        amodal.setFooterHtml(`<button class="btn btn-success" onclick="sales.saveAssetGroup()">SAVE</button>`)
    }

    saveAssetGroup() {
        let id = ['g_name','mypk'];
        if(anton.validateInputs(id)){
            let payload = {
                module:'asset_group',
                data:anton.Inputs(id)
            };
            kasa.confirm(api.call('PUT',payload,'/cmms/api/')['message'],1,'here')
        } else {
            kasa.error("Invalid FOrm")
        }
    }

    getAssetGroup(pk='*'){
        let payload = {
            module:'asset_group',
            data:{
                target:'*'
            }
        }

        return  api.call('VIEW',payload,'/cmms/api/')
    }

    // load asset groups for asset creating

}

const sales = new Sales()