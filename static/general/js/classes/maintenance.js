class Maintenance {
    constructor() {
        this.api_interface = '/maintainance/api/'
    }
    newScreen() {
        let form = "";
        form += fom.text('title', '', true);
        form += fom.textarea('description', 10, true)


        amodal.setBodyHtml(form);
        amodal.setTitleText("ADDING NEW MAINTAINED SERVICE");
        amodal.setFooterHtml(`<button onclick="maintenance.saveNew()" class="btn btn-success w-100">SAVE</button>`)
        amodal.show()
    }

    saveNew() {
        let ids = ['asset', 'title', 'mypk', 'evidence', 'detail'];
        if (anton.validateInputs(ids)) {
            api.payload['module'] = 'maintenance_request';
            api.payload['data'] = anton.Inputs(ids);
            api.payload['data']['analyse'] = ""

            let response = api.call('PUT', api.payload, '/maintainance/api/');
            if (anton.IsRequest(response)) {
                let message = response.message
                $('#entry_no').val(message);
                $('#main_evidence').submit()
            } else {
                kasa.response(response)
            }
        } else {
            kasa.error("Fill All Fields")
        }
    }

    update_maintenance() {

        let form = "";

        form += fom.text('title', '', true);
        form += fom.textarea('description', 4, true);

        amodal.setBodyHtml(form);
        amodal.setTitleText("UPDATE RECORDS");
        amodal.setFooterHtml(`<button onclick="maintenance.updateRecord()" class="btn btn-success w-100">SAVE</button>`);
        amodal.show()
    }

    updateRecord() {
        let ids = ['maintenance', 'mypk', 'title', 'description'];
        if (anton.validateInputs(ids)) {
            api.payload['module'] = 'maintenance_log';
            api.payload['data'] = anton.Inputs(ids);

            let response = api.call('PUT', api.payload, '/maintainance/api/');
            kasa.confirm(response['message'], 1, 'here');

        } else {
            kasa.error("Fill All Fields");
        }
    }

    close_screen() {

        Swal.fire({
            title: 'Are you sure?',
            text: 'You won\'t be able to revert this!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, proceed!',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            // Check if the user clicked the confirm (yes) button
            if (result.isConfirmed) {

                let form = '';
                form += fom.textarea('message', 5, true)
                amodal.setTitleText("CLOSING MESSAGE")
                amodal.setBodyHtml(form);
                amodal.setFooterHtml(`<button onclick="maintenance.close()" class="btn btn-success w-100">CLOSE</button>`);
                amodal.show()

            }
        });

    }

    close() {
        let ids = ['mypk', 'maintenance', 'message'];
        if (anton.validateInputs(ids)) {
            api.payload['data'] = anton.Inputs(ids);
            api.payload['module'] = 'close';

            let response = api.call('PATCH', api.payload, '/maintainance/api/');
            kasa.confirm(response['message'], 1, 'here');

        } else {
            kasa.error("Fill Required Fields")
        }
    }

    getGroup(key = '*') {
        let payload = {
            module: 'maintenance_asset_group',
            data: {
                key: key
            }
        }
        return api.call('VIEW', payload, this.api_interface);


    }

    new_asset_group_screen() {
        let form = '';
        form += fom.text('name', 'Group Name', true);
        amodal.setTitleText("New Maintainance Asset");
        amodal.setBodyHtml(form);
        amodal.setFooterHtml(`<button onclick="maintenance.save_asset_group()" class="btn btn-success">SAVE</button>`);
        amodal.show();

    }

    save_asset_group() {
        let ids = ['mypk', 'name'];
        if (anton.validateInputs(ids)) {
            let payload = {
                module: 'maintenance_asset_group',
                data: anton.Inputs(ids)
            }
            kasa.confirm(
                api.call('PUT', payload, this.api_interface)['message'], 1, 'here'
            )
        } else {
            kasa.error("Fill All Fields")
        }
    }

    new_asset_sub_screen(name) {
        let form = '';
        form += fom.text('group', '', true);
        form += fom.text('sub_group', '', true);

        amodal.setBodyHtml(form);
        $('#group').prop('disabled', true);
        $('#group').val(name);
        amodal.setTitleText(`Crete Sub Group Under ${name}`);
        amodal.setFooterHtml(`<button onclick="maintenance.save_sub_group()" class="btn btn-success btn-sm">SAVE</button>`)
        amodal.show()
    }

    save_sub_group() {
        let id = ['mypk', 'group', 'sub_group'];
        if (anton.validateInputs(id)) {
            let payload = {
                module: 'maintenance_asset_sub_group',
                data: anton.Inputs(id)
            };
            console.table(payload)
            kasa.confirm(api.call("PUT", payload, this.api_interface)['message'], 1, 'here');
            loadXSubs($('#group').val())
        } else {
            kasa.error("Fill ALl Fields");
        }
    }



    loadAssetScreen(key) {
        console.log(key)
        let payload = {
            module: 'maint_asset',
            data: {
                key: key
            }
        }

        let asset = api.call('VIEW', payload, this.api_interface)
        if (anton.IsRequest(asset)) {
            let details = asset.message;
            $('#group').val(details.group.name);
            $('#sub_group').val(details.subgroup.name);
            $('#sku').val(details.barcode);
            $('#name').val(details.name)
            $('#location').val(details.location.descr)
            $('#brand').val(details.brand)
            $('#origin').val(details.origin)
            $('#color').val(details.color)
            $('#previewImage').prop('src', details.image)

            let next, previous;
            next = details.next;
            previous = details.previous;
            if (next !== 0) {
                $('#next').prop('disabled', false);
                $('#next').val(next)
            } else {
                $('#next').prop('disabled', true);
            }
            if (previous !== 0) {
                $('#previous').prop('disabled', false);
                $('#previous').val(previous)
            } else {
                $('#previous').prop('disabled', true);
            }
            console.table(details)
        } else {
            kasa.response(asset)
        }
    }

    dataURLtoBlob(dataURL) {
        var parts = dataURL.split(';base64,');
        var contentType = parts[0].split(':')[1];
        var raw = window.atob(parts[1]);
        var rawLength = raw.length;
        var uInt8Array = new Uint8Array(rawLength);

        for (var i = 0; i < rawLength; ++i) {
            uInt8Array[i] = raw.charCodeAt(i);
        }

        return new Blob([uInt8Array], { type: contentType });
    }

    save_new_asset() {
        let ids = ['group', 'sub_group', 'sku', 'name', 'location', 'brand', 'origin', 'color', 'image', 'mypk'];
        if (anton.validateInputs(ids)) {
            let payload = {
                module: 'maintenance_asset',
                data: anton.Inputs(ids)
            };
            var fileInput = $('#image')[0];
            var file = fileInput.files[0];
            var reader = new FileReader();
            reader.onload = function (e) {
                var fileDataUrl = e.target.result;
                var blob = maintenance.dataURLtoBlob(fileDataUrl);
                payload.data['image'] = blob;
                console.table(blob)
            }

            reader.readAsDataURL(file);
            console.table(payload)


            let send = api.call('PUT', payload, this.api_interface);
            if (anton.IsRequest(send)) {
                let pk = send.message;
                $('#pk').val(pk);
                $('#upload_form').submit()
                kasa.info("UPLOADING IMAGE....")

            }

        } else {
            kasa.error('Fill All Fields')
        }
    }

    getMentanance(pk) {
        let payload = {
            module: 'maintenance',
            data: {
                key: pk
            }
        };
        return api.call('VIEW', payload, this.api_interface)
    }

    // generating work order
    generateWoScreen() {
        let form = '';


        let users = user.allUsers();
        if (anton.IsRequest(users)) {
            let options = `<option value = ''>SELECT TECHNICIAN</option>`;
            let uss = users['message'];
            for (let index = 0; index < uss.length; index++) {
                const element = uss[index];
                options += `<option value = '${element.pk}'>${element.fullname}</option>`;

            }
            form += fom.textarea('analysis', 5, true);
            form += fom.select('technician', options, '', true);
            amodal.setBodyHtml(form);
            amodal.setTitleText('Generating Work Order');
            amodal.setFooterHtml(`<button class='btn btn-success' onclick='ment.generateWO()'>SAVE</button>`);
            amodal.show();

        } else {
            kasa.response(users);
        }


    }

    generateWO() {
        let idsx = ['mypk', 'technician', 'analysis', 'entry_no'];

        if (anton.validateInputs(idsx)) {
            let payload = {
                module: 'generate_wo',
                data: anton.Inputs(idsx)
            };

            console.table(payload)

            let generate = api.call('PUT', payload, this.api_interface); // send payload to api

            if (anton.IsRequest(generate)) {
                // load work request again
                amodal.close()
                kasa.info(generate.message['msg']);
                loadMaintenance(`${generate.message['wr_pk']}`)

            } else {
                kasa.response(generate);
            }
        } else {
            kasa.error("Invalid Form");
        }
    }

    getWorkOrder(pk = '*') {
        let payload = {
            module: 'work_order',
            data: {
                key: pk
            }
        };

        return api.call('VIEW', payload, this.api_interface)
    }

    loadWo(pk) {
        let work_order_reponse = this.getWorkOrder(pk);
        if (anton.IsRequest(work_order_reponse)) {
            let wo = work_order_reponse.message[0];
            
            let wr = wo['wr'];
            let asset = wr['asset'];
            x_ass = asset
            $('#wo_no').val(wo['entry_no'])
            $('#status').val(wo['is_open']);
            $('#date_time').val(`${wo['meta']['date_created']} ${wo['meta']['time_created']}`)
            $('#location').val(wr['record']['location']);
            $('#technician').val(wo['technician']['name'])
            $('#wr_no').val(wr['record']['entry_no']);
            $('#asset').val(asset['name']);
            $('#owner').val(wo['owner'])
            let evidence = wr['record']['evidence']
            $("#evidence").attr("src", `/${evidence}`);
            $('#analysis').html(wo['analyse']);
            $('#issue').html(wr['record']['description']);

            // next previous
            let next = wo['next'];
            let previous = wo['prev'];
            if (next > 0) {
                $('#next').val(next);
                $('#next').prop('disabled', false);
            } else {
                $('#next').prop('disabled', true)
            }
            if (previous > 0) {
                
                $('#previous').val(previous);
                $('#previous').prop('disabled', false);
            } else {
                
                $('#previous').prop('disabled', true)
            }


            // materials
            let materials = wo['materials'];
            let mat_av, mats;
            mat_av = materials['available'];
            if(mat_av){
                $('#material_request').prop('disabled',false)
            } else {
                $('#material_request').prop('disabled',true)
            }
            if (true) {
                let mat_rows = "";
                mats = materials['materials'];
                for (let index = 0; index < mats.length; index++) {
                    const element = mats[index];
                    mat_rows += `
                        <tr>
                            <td>${element['name']}</td>
                            <td>${element['description']}</td>
                            <td>${element['quantity']}</td>
                            <td>${element['unit_price']}</td>
                            <td>${element['total']}</td>
                        </tr>
                    `
                }
                $('#mat_body').html(mat_rows)
            }

            // attackments
            let attachments = wo['attachments'];
            let atts = attachments['attachments'];
            console.table(atts)
            let tr = "";
            for (let atx = 0; atx < atts.length; atx++) {
                const attx = atts[atx];
                let f = attx['file'];
                let f_type = "unknown/unknown";
                // console.table(f)
                if(f !== 'null'){
                    if(f['type'] != null){
                        let f_type= f['type'].split('/')[f['type'].split('/').length - 1]
                    }
                }
                

                
                tr += `
                
                <tr>
                    <td>${attx['type']}</td>
                    <td>${attx['description']}</td>
                    <td><a onclick="anton.viewFile('${f['url']}','${f_type}','${attx['type']}')" href="javascript:void(0)">${f['name']}</a></td>
                </tr>
                `;
            }
            $('#wo_attches').html(tr);


        } else {
            kasa.response(work_order_reponse)
        }
    }

    showWoAsset() {
        let ass = x_ass;
        console.table(ass)
        let htm = `
            <p><strong>Barcode</strong> : ${ass['sku']}</p>
            <p><strong>Group</strong> : ${ass['group']}</p>
            <p><strong>Sub Group</strong> : ${ass['subgroup']}</p>
            <p><strong>Name</strong> : ${ass['name']}</p>
            <p><strong>Brand</strong> : ${ass['brand']}</p>
            <p><strong>Origin</strong> : ${ass['origin']}</p>
            <p><strong>Location</strong> : ${ass['location']['name']}</p>
        `;
        amodal.setTitleText('Asset Details');
        amodal.setBodyHtml(htm);
        amodal.show()
    }

    saveWoMaterial() {
        let ids = ['wo_no', 'mat_name', 'mat_descr', 'price', 'quantity', 'mypk'];
        if (anton.validateInputs(ids)) {
            let payload = {
                'module': 'wo_material',
                data: anton.Inputs(ids)
            }
            let save = api.call('PUT', payload, this.api_interface);
            if (anton.IsRequest(save)) {
                // load entry
                let pk = save.message
                ment.loadWo(pk)
                kasa.success("Material Saved");
                amodal.hide()
            } else {
                kasa.response(save)
            }
        } else {
            kasa.error("Fill All Fields")
        }
    }

    woAttachmentForm() {
        let form = `
            <form id='att_evi' action='/maintainance/upload-wo-attachment/' method='post'enctype="multipart/form-data">
                <label for='type'>TYPE</label>
                <select class='form-control mb-2 rounded-0' name='type' id='type'>
                    <option value='invoice'>Invoice</option>
                    <option value='evidence'>Evidence</option>
                </select>
                <input type='hidden' id='wo_att_no' name='wo_att_no' >

                <label for='wo_att_descr'>Description</label>
                <input id='wo_att_descr' name='wo_att_descr' class='form-control rounded-0 mb-2' required>

                <label for='file'>FILE</label>
                <input type='file' id='file' name='file' required class='form-control rounded-0' >
            </form>
        `;

        amodal.setBodyHtml(form);
        amodal.setTitleText('Upload Attachment');
        amodal.setFooterHtml(`<button onclick="ment.saveWoAttachment()" class='btn btn-sm btn-success w-100'>UPLOAD</button>`);
        amodal.show()
        $('#wo_att_no').val($('#wo_no').val())
    }

    saveWoAttachment() {
        console.log("Hello")
        // Serialize the form data
        var formData = new FormData($("#att_evi")[0]);
        console.table(formData)

        // Make an AJAX request
        $.ajax({
            type: 'POST',
            url: '/maintainance/upload-wo-attachment/',  // Replace with your actual API endpoint
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                console.table(response);
                // Handle success response
                if (anton.IsRequest(response)) {
                    let pk = response['message']
                    ment.loadWo(pk)
                    kasa.success("Attachment Uploaded")
                    amodal.hide()
                } else {
                    kasa.response(response)
                }

            },
            error: function (error) {
                // Handle error
                console.error('Error:', error);
            }
        });

    }

    generateMaterialRequest(){
        let payload = {
            module:'generate_wo_material_request',
            data:{
                wo:$('#wo_no').val(),
                mypk:$('#mypk').val()
            }
        };

        let generate = api.call('VIEW',payload,this.api_interface);
        if(anton.IsRequest(generate)){
            console.table(generate)
            anton.viewFile(`/${generate.message}`,'x/pdf')
            // kasa.success('lets go');
        } else {
            kasa.response(generate);
        }
    }

    // close work order
    closeWorkOrderscreen(){
        let form = "";
        form += fom.textarea('clossing_message','',true)
        amodal.setBodyHtml(form);
        amodal.setTitleText("COSING")
        amodal.setFooterHtml(`<button onclick='ment.closeWo()' class='btn btn-danger w-100'>CLOSE</button>`)
        amodal.show()
        
    }

    closeWo(){
        let ids = ['wo_no','clossing_message','mypk'];
        if(anton.validateInputs(ids)){
            let payload = {
                module:'close_wo',
                data:anton.Inputs(ids)
            };

            let xlos = api.call('PATCH',payload,this.api_interface);
            kasa.confirm(xlos.message,1,'here')
        } else {
            kasa.error("Fill All Fields")
        }
        
    }

    woReport(){
        let payload = {
            module:'gen_wo_report',
            data:{
                'wo_no':$('#wo_no').val()
            }
        };

        let gen = api.call('VIEW',payload,this.api_interface);
        if(anton.IsRequest(gen)){
            let url = `/${gen.message}`
            anton.viewFile(url,'pdf/pdf')
        } else {
            kasa.response(gen)
        }
    }

    // end of generating work order
    
}

const maintenance = new Maintenance();
const ment = new Maintenance();