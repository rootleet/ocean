class Api {

    constructor() {
        this.payload = {
            module:'',
            data:{}
        }
    }
    call(method,data,link='/apiv2/'){
        // console.log(JSON.stringify(data))
        // let link = interface
        // console.table(link)
        var result = {
            'status_code':0,
            'message':'Not Sent To Backend'
        };
        $.ajax({
            url:link,
            type: method,
            contentType: 'application/json; charset=utf-8',
            processData: false,
            async: false,
            dataType: 'html',
            data:JSON.stringify(data),
            // dataType: "json",
            success: function (response) {

                result =  JSON.parse(response)
                // console.table(response)

            },
            error: function (error)
            {

                result = error
            }
        })

        // console.table(result['responseText'])
        return result
    }

    view(data){
        return this.call('VIEW',data)
    }

    put(data){
        return this.call('PUT',data)
    }

    patch(data){
        return this.call('PATCH',data)
    }

    delete(data){
        return this.call('DELETE',data)
    }
}

const api = new Api()