class Retail {
    boldUploadScreen(){

        // get groups
        let groups = api.call('VIEW',{module:'bolt_group',data:{'pk':'*'}},'/retail/api/')
        if(groups['status_code'] === 200){
            let group_options = `<option value="0">NEW</option>`;
            let grps = groups['message'];
            for(let g = 0; g < grps.length; g++){
                let group = grps[g];
                group_options += `<option value="${group['pk']}">${group['name']}</option>`;

            }

            let form = `
                <a href="https://">Download Template</a> <br>
                <label for="group">GROUP</label>
                <select onchange="retail.uploadGroupSelection()" id="group" class="form-control rounded-0 mb-2">${group_options}</select>
                <label for="group_name">GROUP NAME</label>
                <input type="text" name="group_name" id="group_name" class="form-control mb-2 rounded-0">
                <label for="file">ITEMS FILE</label>
                <input type="file" name="" id="file" accept="text/csv" class="form-control mb-2 rounded-0">
                <button onclick="retail.boltUpload()" type="submit" class="btn btn-success w-100">PROCESS</button>
            `;
            amodal.setTitleText(`Upload Batch Files`);
            amodal.setBodyHtml(form);
            amodal.show()
        } else {
            kasa.error(groups['message']);
        }

    }

    uploadGroupSelection(){
        let text = $('#group').find(':selected').text();
        let grou_name = $('#group_name')
        if(text === 'NEW'){
            grou_name.val('');
            grou_name.prop('disabled',false);
            grou_name.prop('focused',true);
        } else {
            grou_name.prop('disabled',true);
            grou_name.prop('focused',false);
            grou_name.val(text)
        }

    }

    boltUpload(){

        if(anton.validateInputs(['group_name'])){
            let group_req = api.call(
            'PUT',{'module':'bolt_group',data:{name:$('#group_name').val()}},'/retail/api/'
            );

            if(group_req['status_code'] === 200){
                let group = group_req['message'];
                const file = document.getElementById('file').files[0];
                if(!file) {
                    alert('PLEASE SELECT A FILE');
                    return;
                }

                const reader = new FileReader();
                reader.onload = e => {

                    for(const line of e.target.result.split('\r')){
                        const this_line = line.split(',');
                        let barcode,name,price,spintex,nia,osu;
                        barcode = this_line[0].replace('\n','');
                        name = this_line[1];
                        price = this_line[2];
                        spintex = this_line[3];
                        nia = this_line[4];
                        osu = this_line[5];

                        let payload = {
                            'module':'bolt_item',
                            data:{
                                group:group,
                                barcode:barcode,
                                item_des:name,
                                price:price,
                                stock_nia:nia,
                                stock_spintex:spintex,
                                stock_osu:osu
                            }
                        };

                        let prd_put = api.call('PUT',payload,'/retail/api/')

                        console.table(prd_put);
                    }
                }
                reader.readAsText(file)
                kasa.confirm('ITEMS ADDED',1,'here')
            } else {
                kasa.error(group_req['message'])
            }
        } else {
            kasa.error("ALL FIELDS ARE REQUIRED")
        }




    }

    checkPrices(){
       loader.show();
        let payload = {
            module:'price_change',
            data: {
                'send':'no'
            }
        };

        let request = api.call('VIEW',payload,'/retail/api/');

        if(anton.IsRequest(request)){
            let message = request['message'];
            console.table(message);
            let table = `
                <table class="table table-sm table-bordered">
                    <thead><tr><th>PART</th><th>CHANGES</th><th>FILE</th></tr></thead>
                    <tbody>
                        <tr><td>PRICE CHANGE</td><td>${message['price_change']['count']}</td><td><a href="/${message['price_change']['file']}"><i class="bx bx-download"></i></a></td></tr>
                        <tr><td>SPINTEX STOCK</td><td>${message['spintex_stock_change']['count']}</td><td><a href="/${message['spintex_stock_change']['file']}"><i class="bx bx-download"></i></a></td></tr>
                        <tr><td>NIA STOCK</td><td>${message['nia_stock_change_file']['count']}</td><td><a href="/${message['nia_stock_change_file']['file']}"><i class="bx bx-download"></i></a></td></tr>
                        <tr><td>OSU STOCK</td><td>${message['osu_stock_change_file']['count']}</td><td><a href="/${message['osu_stock_change_file']['file']}"><i class="bx bx-download"></i></a></td></tr>

                    </tbody>
                </table>
            `;

            amodal.setBodyHtml(table);
            amodal.setTitleText("PRICE AND STOCK UPDATE");
            loader.hide();
            amodal.show();
        } else {
            kasa.error(request['message'])
        }

    }

    markProducts(){
        let payload = {
            module:'price_update',
            data: {

            }
        };

        if(confirm("Are you Sure?")){
             let request = api.call('PATCH',payload,'/retail/api/');
            kasa.confirm(request['message'],1,'here')
        }

    }


    exportItems(pk) {
        $('#loader').show()

        let payload = {
            module:'export_items',
            data: {
                'format':'excel',
                key:pk
            }
        };
        let request = api.call('VIEW',payload,'/retail/api/');
        if(anton.IsRequest(request)){

            kasa.html(`<a href="/${request['message']}">Download File</a>`)

        } else {
            kasa.error(request['message'])
        }

        $('#loader').hide()
    }

    loadProducts() {
        let payload = {
            "module":"retail_products",
            "data":{
                "doc":"json"
            }
        }

        let response = api.call('VIEW',payload,'/retail/api/');
        if(anton.IsRequest(response)){
            let products = response['message'];
            let tr = "";
            for (let p = 0; p < products.length; p++) {
                let product = products[p];
                let group,subgroup,barcode,name,price,is_on_bolt;
                group = product['group'];
                subgroup = product['sub_group'];
                barcode = product['barcode'];
                name = product['name'];
                price = product['price'];
                is_on_bolt = product['is_on_bolt']
                tr += `
                    <tr><td>${group}</td><td>${subgroup}</td><td>${barcode}</td><td>${name}</td><td>${price}</td><td>${is_on_bolt}</td></tr>
                `;
            };
            let table = `
                <table class="table table-hover table-sm"><thead>
                <tr>
                    <th>GROUP</th>
                    <th>SUB GROUP</th>
                    <th>BARCODE</th>
                    <th>NAME</th>
                    <th>INVENTORY PRICE</th>
                    <th>IS_ON_BOLT</th>
                </tr>
            </thead>
            <tbody id="tbody">
            </tbody>${tr}</table>
            `;

            $('.card-body').html(table)
        } else {
            $('#pagebody').html(response['message'])
        }
    }

    export_retail_products(pk='*') {
        $('#loader').show()

        let payload = {
            module:'retail_products',
            data: {
                'doc':'excel',
                product:pk
            }
        };
        let request = api.call('VIEW',payload,'/retail/api/');
        if(anton.IsRequest(request)){

            kasa.html(`<a href="/${request['message']}">Download File</a>`)

        } else {
            kasa.error(request['message'])
        }

        $('#loader').hide()
    }

    // STOCK SECTION
    retrieveSockFreezeScreen(){
        let form = ``;
        form += fom.text('entry','frozen entry in mycom',true)
        amodal.setTitleText("Retrieve Frozen")
        amodal.setBodyHtml(form);
        amodal.setFooterHtml(`<button onclick='retail.retrieveStock()' class='w-100 btn btn-success'>RETIRVE</button>`)
        amodal.show()
    }

    retrieveStock(){
        let ids = ['mypk','entry'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:'retrieve_frozen_stock',
                data:anton.Inputs(ids)
            }

            let ret = api.call("PUT",payload,'/retail/api/');
            if(anton.IsRequest(ret)){
                console.table(ret)
            } else {
                kasa.response(ret)
            }
            
        } else {
            kasa.error("Fill All Fields")
        }
    }
    // END OF STOCK SECTION
}

const retail = new Retail();