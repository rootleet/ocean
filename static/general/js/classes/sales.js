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

    newOrigin() {
        let form  = `
            <label for="country">Country</label>
            <input id="country" class="form-control rounded-0">
        
        `;

        amodal.setBodyHtml(form);
        amodal.setTitleText("New Car Origin")
        amodal.setFooterHtml(`<button class="btn btn-success w-100" onclick="sales.saveOrigin()">SAVE</button>`)
        amodal.show()
    }

    saveOrigin() {

        let ids = ['country','mypk'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:'CarOrigin',
                data:anton.Inputs(ids)
            }
            amodal.hide(true)
            kasa.response(api.call('PUT',payload,'/cmms/api/'))
            this.loadOrigins()
        } else {
            kasa.error("Invalid Form")
        }
    }

    loadOrigins() {
        let origins = this.getOrigins('*');
        if(anton.IsRequest(origins)){
            let orgs = origins['message'];
            let tr = ''
            for(let o = 0; o < orgs.length; o++){
                let origin = orgs[o];
                tr += `<tr><td>${origin['country']}</td></tr>`
            }

            $('#origins_table').html(tr)
        } else {
            kasa.response(origins)
        }
    }

    getOrigins(s = '*') {
        return api.call('VIEW',{
            module:'CarOrigin',
            data:{
                key:'*'
            }
        },'/cmms/api/')
    }

    // manufacturer
    newManufacturer() {
        let form = '';

        // make origin
        let origin_reponse = this.getOrigins('*');
        let orition_options = `<option value="">Select Origin</option>`
        if(anton.IsRequest(origin_reponse)){
            // load origins
            let origins = origin_reponse['message'];
            for(let o = 0; o < origins.length; o++){
                let origin = origins[o];

                orition_options += `<option value="${origin['pk']}">${origin['country']}</option>`
            }

            form += fom.select('o_key',orition_options,true)
            form += fom.text('name','Manufacturer Name',true);

            amodal.setTitleText("New Manufacturer")
            amodal.setBodyHtml(form)
            amodal.setFooterHtml(`<button class="btn btn-success w-100" onclick="sales.saveManufacturer()">SAVE</button>`)
            amodal.show()
        } else {
            kasa.response(origin_reponse)
        }
    }

    saveManufacturer() {
        let ids = ['name','o_key','mypk'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:'CarManufacturer',
                data:anton.Inputs(ids
                )
            };
            amodal.hide()
            kasa.response(api.call('PUT',payload,'/cmms/api/'))
            this.loadManufacturer()
        } else {
            kasa.error("invalid Form")
        }
    }

    loadManufacturer() {
        let man_resp = this.getManufacturer();
        if(anton.IsRequest(man_resp)){
            // load screen
            let mans = man_resp['message'];

            let tr = ``;
            for(let m = 0; m < mans.length; m++){
                let man = mans[m];
                tr += `<tr><td>${man['origin']}</td><td>${man['name']}</td></tr>`
            }

            $('#man_table').html(tr)
        } else {
            kasa.response(man_resp)
        }
    }

    getManufacturer(key = '*') {
        return api.call('VIEW',{
            module:'CarManufacturer',
            data:{
                key:key
            }
        },'/cmms/api/');
    }

    // suppliers
    newSupplier(){
        let form = ``;

        let origin_reponse = this.getOrigins('*');
        let orition_options = `<option value="">Select Origin</option>`
        if(anton.IsRequest(origin_reponse)){
            // load origins
            let origins = origin_reponse['message'];
            for(let o = 0; o < origins.length; o++){
                let origin = origins[o];

                orition_options += `<option value="${origin['pk']}">${origin['country']}</option>`
            }

            form += fom.select('o_key',orition_options,true)
            form += fom.text('name','',true);
            form += fom.text('email','',true);
            form += fom.text('phone','',true);
            form += fom.text('website','',true);


            amodal.setTitleText("New Manufacturer")
            amodal.setBodyHtml(form)
            amodal.setFooterHtml(`<button class="btn btn-success w-100" onclick="sales.saveSupplier()">SAVE</button>`)
            amodal.show()
            $('#website').val('www.none.com')
        } else {
            kasa.response(origin_reponse)
        }
    }

    saveSupplier() {
        let ids = ['mypk','o_key','name','phone','email','website'];
        if(anton.validateInputs(ids)){
            kasa.response(api.call('PUT',{
                module:'CarSupplier',data:anton.Inputs(ids)
            },'/cmms/api/'))
            amodal.hide()
            this.loadSupplier()
        } else {
            kasa.error("Invalid Form")
        }
    }

    loadSupplier(){
        let supplier_response = this.getSupplier();
        if(anton.IsRequest(supplier_response)){
            // load screen
            let mans = supplier_response['message'];

            let tr = ``;
            for(let m = 0; m < mans.length; m++){
                let man = mans[m];
                tr += `<tr><td>${man['origin']}</td><td>${man['name']}</td></tr>`
            }

            $('#supplier_table').html(tr)
        } else {
            kasa.response(supplier_response)
        }
    }

    getSupplier(key = '*') {
        return api.call('VIEW',{module:'CarSupplier',data:{key:key}},'/cmms/api/');
    }

    loadAsset(asset_key) {
        let asset = this.getAsset(asset_key);
        if(anton.IsRequest(asset)){
            let asset_msg = asset['message'][0];

            $('#name').val(asset_msg['name'])
            $('#manufacturer').val(asset_msg['manufacturer'])
            $('#supplier_origin').val(asset_msg['sup_origin'])
            $('#origin').val(asset_msg['man_origin'])
            $('#supplier').val(asset_msg['supplier'])
            $('#created_date').val(asset_msg['created_date'])
            $('#created_by').val(asset_msg['created_by'])

            next = asset_msg['next']
            previous = asset_msg['previous']
            asset_key = asset_msg['pk']

            if(next > 0){
                $('#next').prop('disabled',false)
            } else {
                $('#next').prop('disabled',true)
            }

            if(previous > 0){
                $('#previous').prop('disabled',false)
            } else {
                $('#previous').prop('disabled',true)
            }

            // load modules
            let asset_modules_response = api.call('VIEW',{
                module:'ModelsByCar',
                data:{
                    'key':asset_key
                }
            },'/cmms/api/');

            if(anton.IsRequest(asset_modules_response)){
                let models = asset_modules_response['message'];
                let tr = ``;
                for(let m = 0; m< models.length; m++){
                    let model = models[m];
                    tr += `<tr>
                                <td><a href="#">${model['model_name']}</a></td>
                                <td>${model['year']}</td>
                                <td>0</td>
                                <td>${model['docs']}</td>
                                <td>${model['price']}</td>
                                <td>
                                    <div class="dropdown">
                                      <button class="btn btn-secondary" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                        <i class="fas fa-angle-down"></i>
                                      </button>
                                      <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                                        <a class="dropdown-item" onclick="sales.changeModelPrice(${model['pk']})" href="javascript:void(0)">Change Price</a>
                                        <a class="dropdown-item" onclick="windowPopUp('/cmms/sales/spec/${model.pk}/','SPEC',500,678)" href="javascript:void(0)">Specs</a>
                                        <a class="dropdown-item" onclick="sales.generateProfoma(${model['pk']})" href="javascript:void(0)">Generate Profoma</a>
                                      </div>
                                    </div>
                                
                                </td>
                            </tr>`
                }
                $('#models').html(tr)
            } else {
                kasa.error(`Could not load car models ${asset_modules_response['message']}`)
            }
        } else {
            kasa.response(asset)
        }
    }

    getAsset(asset_key) {
        return api.call("VIEW",{module:'Car',data:{key:asset_key}},'/cmms/api/');
    }

    getAssetModels(asset_key){
        return api.call("VIEW",{module:'ModelsByCar',data:{key:asset_key}},'/cmms/api/');
    }

    changeModelPrice(model_key) {
        let form = `<input type="hidden" id="model_key" >`;
        form += fom.text('new_price','',true);
        amodal.setTitleText("Changing Model Price")
        amodal.setBodyHtml(form)
        amodal.setFooterHtml(`<button onclick="sales.saveModelPrice()" class="btn btn-success w-100">SAVE NEW PRICE</button>`)
        amodal.show()
        $('#model_key').val(model_key)
    }

    saveModelPrice() {
        let ids = ['new_price','model_key'];
        if(anton.validateInputs(ids)){
            kasa.response(
                api.call('PATCH',{
                    module:'ModelPriceChange',
                    data:anton.Inputs(ids)
                },'/cmms/api/')
            );
            amodal.hide()
            this.loadAsset(asset_key)
        } else {
            kasa.error("Invalid Form")
        }
    }

    newModuleSpec(model_pk) {
        let options = `<option value="int">interior</option>
                    <option value="ext">Exterior</option>
                    <option value="tech">Technical</option>`;
        let form = `<input type="hidden" id="model" value="${model_pk}">`
        form += fom.select('part',options,true)
        form += fom.text('name','',true);
        form += fom.text('value','',true)
        amodal.setTitleText("New Spec")
        amodal.setBodyHtml(form)
        amodal.setFooterHtml(`<button onclick="sales.saveModelSpecification()" class="btn btn-success w-100">SAVE SPEC</button>`)
        amodal.show()
    }

    saveModelSpecification() {
        let ids = ['mypk','model','name','value','part'];
        if(anton.validateInputs(ids)){
            kasa.response(
                api.call('PUT',{
                    module:"CarSpecification",
                    data:anton.Inputs(ids)
                },'/cmms/api/')
            );
            amodal.hide()
            let part = $('#section').val();
                loadModelSpecs(model_key,part)
        } else {
            kasa.error("Invalid Form")
        }
    }

    getModelSpecifications(model_key=1,part='*'){
        return api.call('VIEW',{
            "module":"CarSpecification",
            "data":{
                "car_model":model_key,
                part:part,
            }
        },'/cmms/api/')
    }

    editSpecs(pk,key,value) {
        let form = `<input type="hidden" id="pk" value="${pk}">`;
        let options = `<option value="int">interior</option>
                    <option value="ext">Exterior</option>
                    <option value="tech">Technical</option>`;
        form += fom.select('part',options,true)
        form += fom.text('key','',true);
        form += fom.text('value','',true);


        amodal.setTitleText(`Edit ${key}`)
        amodal.setBodyHtml(form)
        amodal.setFooterHtml(`<button onclick="sales.commitSpecsChange()" class="btn btn-success w-100">COMMIT CHANGE</button>`)
        amodal.show()

        $('#key').val(key);
        $('#value').val(value)
    }

    commitSpecsChange() {
        let ids = ['pk','part','key','value'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:"CarSpecifications",
                data:anton.Inputs(ids)
            }

            kasa.response(api.call('PATCH',payload,'/cmms/api/'));
            amodal.hide()
            loadModelSpecs(model_key,$('#section').val())
        } else {
            kasa.error("Invalid Fields")
        }
    }

    generateProfoma(model_pk) {
        // get customers
        let customers = this.salesCustomers('all');
        if(anton.IsRequest(customers)){
            let custs = customers['message']
            let cust_opt = `<option value="">Select Customer</option>`

            for(let c = 0; c< custs.length;c++){
                let customer = custs[c]
                cust_opt += `<option value="${customer.pk}">${customer.company} - ${customer.name}</option>`
            }

            let form = `<input id="model" type="hidden" value="${model_pk}">`;
            form += fom.select('customer',cust_opt,'',true)
            form += fom.text('chassis','',true)
            form += fom.text('quantity','',true)
            form += fom.text('currency','Symbol',true)

            let taxable = `<option value="YES">YES</option><option value="NO">NO</option>`
            form += fom.select('taxable',taxable,'',true)


            amodal.setTitleText("GENERATE PROFORMA")
            amodal.setBodyHtml(form)
            amodal.setFooterHtml(`<button onclick="sales.saveProforma()" class="btn btn-success w-100">GENERATE</button>`)
            amodal.show()
        } else {
            kasa.error(customers['message'])
        }
    }

    newModelScreen() {
        let form = `<input type="hidden" class="form-control" id="car" value="${asset_key}">`
        form += fom.text('model_name','',true)
        form += fom.text('year','',true)
        form += fom.text('price','In basic selling currency not local currency',true)

        amodal.setTitleText("NEW ASSET MODEL")
        amodal.setBodyHtml(form)
        amodal.setFooterHtml(`<button onclick="sales.saveAssetModel()" class="btn btn-success w-100">SAVE</button>`)
        amodal.show()
    }

    saveAssetModel() {
        let ids = ['model_name','car','mypk','price','year']
        if(anton.validateInputs(ids)){
            let payload = {
                module:'CarModel',
                data:anton.Inputs(ids)
            }



            kasa.response(api.call('PUT',payload,'/cmms/api/'));
            this.loadAsset(asset_key)
            amodal.hide()
        } else {
            kasa.error("Invalid Form")
        }
    }

    salesCustomers(key='*') {
        return api.call('VIEW',{
            module:'cmms_sales_customer',
            data:{
                key:key
            }
        },'/cmms/api/');
    }

    saveProforma() {
        let fields = ['mypk','model','currency','taxable','chassis','customer','quantity']
        if(anton.validateInputs(fields)){
            let payload = {
                module:"ProformaInvoice",
                data:anton.Inputs(fields)
            }
            console.table(payload)
            kasa.response(api.call('PUT',payload,'/cmms/api/'));
            amodal.hide()
        } else {
            kasa.error("Invalid Form")
        }
    }

    viewProforma(doc) {
        let payload = {
            "module":"PrintProformaInvoice",
            "data":{
                "key":doc
            }
        }

        let pf = api.call('VIEW',payload,'/cmms/api/')
        if(anton.IsRequest(pf)){
            console.table(pf)
            let doc = pf.message
            anton.viewFile(`/${doc}`)
        } else {
            console.error(pf)
            kasa.response(pf)
        }
    }

    updateProformaSpecs(pk) {
        let payload = {
            "module":"UpdateProformaInvoiceSpec",
            "data":{
                "key":pk,
                "mypk":$('#mypk').val()
            }
        }

        if(confirm('Are you sure you want to reset specifications?')){
            let update = api.call('PATCH',payload,'/cmms/api/')
            if(anton.IsRequest(update)){
                // view file
                this.viewProforma(pk)
            } else {
                kasa.response(update)
            }
        } else {
            kasa.info("Operation Canceled")
        }

    }

    requestProformaApproval(pk) {
        let payload = {
            module:"request_proforma_approval",
            data:{
                'mypk':$('#mypk').val(),
                key:pk
            }
        }

        kasa.response(api.call('PATCH',payload,'/cmms/api/'))
    }

    approveProforma(pk) {
        if(confirm("Are you sure?")){
            let user_pin = prompt("Please auth pin:")
            
            if (user_pin) {
                // authenticat first
                let auth_payload = {
                    module:'doc_app_auth',
                    data:{
                        pin:user_pin,
                        doc_type:'sales_proforms'
                    }
                }

                let auth = api.call('VIEW',auth_payload,'/adapi/');
                if(anton.IsRequest(auth)){
                    let mypk = auth.message
                    let payload = {
                        data:{
                            mypk:$('#mypk').val(),
                            key:pk
                        },
                        module:"approve_proforma"
                    }
        
                    kasa.confirm(
                        api.call('PATCH',payload,'/cmms/api/')['message'],1,'here'
                    )
                } else {
                    kasa.response(auth)
                }
            } else {
                alert("You didn't a pin.");
            }
            
        } else {
            kasa.info("Operation Canceled")
        }

    }

    sendProforma(pk) {
        let payload = {
            module:"send_proforma",
            data:{
                key:pk,
                mypk:$('#mypk').val()
            }
        }

        if(confirm("Are you sure you want to send document?")){
            let send = api.call('PATCH',payload,'/cmms/api/')
            kasa.confirm(send.message,1,'here')
        } else {
            kasa.info("Operation Canceled")
        }
    }

    // end proforma life
    ProformaEOD(pk){
        // create from
        let form  = ``;
        form += fom.select('status',"<option value='YES'>Successful</option><option value='NO'>Failed</option>",true)
        form += fom.textarea('remarks',3,true)

        amodal.setBodyHtml(form)
        amodal.setTitleText("End Of Proforma Life")
        amodal.setFooterHtml(`<button onclick='sales.commitProformaEod(${pk})' class='btn btn-success w-100'>COMMIT</button>`)
        amodal.show()
    }

    commitProformaEod(pk){
        let fields = ['status','remarks','mypk']

        if(anton.validateInputs(fields)){
            let payload = {
                module:'proformaEOD',
                data:anton.Inputs(fields)
            }
            payload.data['proforma'] = pk

            kasa.confirm(
                api.call('PATCH',payload,'/cmms/api/')['message'],1,'here'
            )
        } else {
            kasa.error("Invalid Form")
        }
    }
}

const sales = new Sales()