class Api {

    call(method,data){
        // console.log(JSON.stringify(data))
        let link = `/apiv2/`
        // console.table(link)
        var result = 0;
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