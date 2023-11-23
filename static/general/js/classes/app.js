class App {
    assign(){
        let app,pc

        app = $('#app').val()
        pc = $('#pc').val()



        let call = api.put({
            "module":"appcenter",
            "data":{
                "task":"assign",
                "app":app,
                "mach":pc

            }
        })

        alert(call['message'])
    }

    new_app_screen(providers,uni) {
        let form = '';
        form += fom.text('uni','',true)
        form += fom.select('provider',providers);
        form += fom.file('logo','',true);
        form += fom.text('name','',true);
        form += fom.textarea('description',3,true);
        form += fom.text('root','',true);
        form += fom.file('file','',true);
        form += `<hr>`;
        form += fom.button('save','submit')

        let complete_form = `
            <form method="post" action="/appscenter/save_new_app/" enctype="multipart/form-data">${form}</form>
        `;

        amodal.setTitleText("ADD NEW APP")
        amodal.setBodyHtml(complete_form);
        $('#uni').val(uni)
        amodal.show()
    }
}


const app = new App()