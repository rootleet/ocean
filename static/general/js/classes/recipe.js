class Recipe {

    constructor() {
        this.api_interface = '/retail/api/'
    }

    getRecipeGroup(key = '*'){
        let payload = {
            module:'recipe_group',
            data:{
                'key':key
            }
        };

        return api.call('VIEW',payload,this.api_interface)
    }

    loadRecipe() {
        let tr = ""
        let groups = this.getRecipeGroup();
        console.table(groups)
        if(anton.IsRequest(groups)){

            let grps = groups.message
            for(let g = 0; g < grps.length; g++){
                let group = grps[g]
                let prods = group.products
                console.table(prods)
                let is_open = "<span class='badge bg-primary'>OPEN</span>";
                if(group.is_open === false){
                    is_open = "<span class='badge bg-secondary'>CLOSE</span>";
                }
                tr += `
                    
                    <tr>
                                    <td>
                                        <span onclick="location.href='/retail/recipe/group/${group.pk}/'" class="text-primary pointer">${group.name}</span>
                                    </td>
                                    <td>${group.products['counts']}</td>
                                    
                                </tr>
                    
                `
            }

        } else {
            tr = `<tr><td class="text-danger" colspan="3">${groups.message}</td></tr>`
        }

        $('#recipes').html(tr);
    }

    newRecipeGroupScreen(){
        let form = '';
        form += fom.text('name');

        amodal.setBodyHtml(form);
        amodal.setTitleText("NEW RECIPE GROUP");
        amodal.setFooterHtml(`<button onclick="recipe.saveRecipeGroup()" class="btn mx-2 btn-success">SAVE</button>`);
        amodal.show();
    }

    saveRecipeGroup() {
        let id = ['mypk','name'];
        if(anton.validateInputs(id)){
            let payload = {
                module:'recipe_group',
                data:anton.Inputs(id)
            };
            kasa.response(api.call('PUT',payload,this.api_interface));
            this.loadRecipe();
        } else {
            kasa.error("Fill Required FIelds")
        }
    }

    newProductScreen() {
        let screen = "";

        screen += fom.text('name','Product Name');
        
        


        amodal.setBodyHtml(screen);
        amodal.setTitleText("NEW ITEM");
        amodal.setFooterHtml(`<button onclick="recipe.saveProduct()" class="btn btn-success mx-2">SAVE</button>`)
        amodal.show()
    }

    saveProduct() {
        let ids = ['name','mypk'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:'recipe_product',
                data:anton.Inputs(ids)
            };
            payload['data']['barcode'] = $('#name').val()
            payload['data']['gk'] = group_id;
            payload['data']['si_unit'] = 'g'
            
            let save = api.call('PUT',payload,this.api_interface);
            if(anton.IsRequest(save)){
                let product_pk = save.message
                $('#new_product_pk').val(product_pk);
                kasa.info('UPLOADING IMAGE....')
                this.changeProductImage(product_pk);
            } else {
                kasa.response(save);
            }

            // kasa.response(api.call('PUT',payload,this.api_interface));
            // amodal.hide()
            loadRecipeProducts()
        }
    }

    getRecipeProduct(product){
        return api.call('VIEW',{module:'recipe_product',data:{key:product}},this.api_interface)
    }

    loadRecipeItems(product_key){
        console.log(product_key)
        let message = "";
        let products = recipe.getRecipeProduct(product_key);
        console.table(products)

        let tr = "";
        if(anton.IsRequest(products)){

            message = products.message[0];

            let name,recipe,pk,is_open
            is_open = message.is_open
            name = message.name
            pk = message.pk
            recipe = message.recipe_items.list


            $('#prd_name').text(name)
            $('#image').attr('src',`${message.image}`)
            $('#active_product').val(pk)

            $('#prev').prop('disabled',true)
            if(message.previous !== 0){
                $('#prev').prop('disabled',false)
            }

            $('#next').prop('disabled',true)
            if(message.next !== 0){
                $('#next').prop('disabled',false)
            }


            for (let it = 0; it < recipe.length ; it++) {
                let id = it + 1;
                let name,si,qty,item;
                item = recipe[it];
                name = item.name;
                si = item.si_unit;
                qty = item.quantity
                tr += `
                    <tr id="row_${id}">
                    <td>${id}</td>
                    <td><input id="name_${id}" value="${name}" class="form-control rounded-0 form-control-sm" type="text"></td>
         
                    <td><input value="${qty}" id="qty_${id}" style="width: 100px" class="form-control rounded-0 form-control-sm" type="number"></td>
                    <td><span onclick="$('#row_${id}').remove()" class="badge bg-danger pointer">-</span> </td>
                </tr>
                `
            }

            if(is_open === false){
                // disable buttons
                $('#save').prop('disabled',true);
                $('#close').prop('disabled',true);
                $('#newline').prop('disabled',true);
            } else {
                $('#save').prop('disabled',false);
                $('#close').prop('disabled',false);
                $('#newline').prop('disabled',false);
            }

        }

        $('#recipe_items').html(tr)
        next = message.next
        prev = message.previous
    }

    newRecipeLine(){
        let id = $('#recipe_items tr').length + 1

        let html = `
            <tr  id="row_${id}">
                <td>${id}</td>
                <td><input id="name_${id}" class="form-control rounded-0 form-control-sm" type="text"></td>
                
                <td>
                    <input id="qty_${id}" style="width: 100px" class="form-control rounded-0 form-control-sm" type="number">
                </td>
                <td><span onclick="$('#row_${id}').remove()" class="badge bg-danger pointer">-</span> </td>
            </tr>
        `;
        if(anton.validateInputs(['active_product'])){
            $('#recipe_items').append(html);
        } else {
            alert('Select Product')
        }

    }


    saveRecipe() {
        // validate
        let rows = $('#recipe_items tr').length;

        if(rows > 0){
            let pass = true
            let items = []
            for (let i = 1; i <= rows ; i++) {
                let id = i;
                let row_id,name_id,si_id,qty_id;
                row_id = `row_${id}`
                name_id = `name_${id}`
                si_id = `si_${id}`
                qty_id = `qty_${id}`

                let error = anton.validateInputs([name_id,qty_id]);
                if(error === false){
                    pass = false
                    break;
                } else {
                    items.push({
                        'name':$(`#${name_id}`).val(),
                        si_unit:'g',
                        qty:$(`#${qty_id}`).val()
                    })
                }

            }

            if(pass){
                let prod = $('#active_product').val();

                let payload = {
                    module:'recipe_items',
                    data:{
                        mypk:$('#mypk').val(),
                        product:prod,
                        items:items
                    }
                };
                api.call('PUT',payload,this.api_interface)
                this.loadRecipeItems(prod)
                console.table(payload)
            } else {
                kasa.error("Invalid List")
            }
        } else {
            kasa.error("Cannot Save Empty Recipe")
        }
        // console.log(rows);
    }

    close() {
        if(confirm("Are you sure?")){
            let id = ['active_product'];
            let payload = {
                module:'close_recipe',
                data:{
                    prod_key:$('#active_product').val()
                }
            };
            if(anton.validateInputs(id)){
                kasa.response(api.call('PATCH',payload,this.api_interface))
            } else {
                kasa.error("No Active Product")
            }
        } else {
            kasa.info('Operation Cancelled')
        }
    }

    exportGroup(pk=null) {
        let payload = {
            'module':'export_recipe_group',
            data:{
                'group':pk
            }
        }

        let expt = api.call('VIEW',payload,this.api_interface);
        if(anton.IsRequest(expt)){
            kasa.html(`<a href="${expt.message}">DOWNLOAD</a>`)
        } else {
            kasa.response(expt)
        }
    }

    changeProductImage(pk){
        let form = `
            <form action='/retail/recipe/upload_item_image/' method="post" enctype="multipart/form-data" id='change_product_image'>
                <input type='hidden' name='prod_pk' require id='prod_pk' value = '${pk}'>
                <input name='prod_image' type='file' accept='images/*' require id='prod_image' class='form-control rounded-0' />
                <hr>
                <button type='submit' class='btn btn-sm rounded-0 btn-success'>SAVE</button>
            </form>
        `;

        amodal.setTitleText("Change Product Image")
        amodal.setBodyHtml(form);
        amodal.setFooterHtml('')
        amodal.show()
    }



}

const recipe = new Recipe()