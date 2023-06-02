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
}


const app = new App()