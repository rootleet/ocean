class Products {

    GetProduct(barcode)
    {
        var result = 0;
        let form_data;
        form_data = {
            'for':'get_product',
            'query':barcode
        }

        $.ajax({
            url:$('#search_url').val(),
            data:form_data,
            'async': false,
            'type': "GET",
            'global': false,
            'dataType': 'html',
            success: function (response){
                result = response;
            }
        })

        return result;

    }

    GetProductPacking(barcode)
    {
        let form_data;
        form_data = {
            'for':'get_prod_packing',
            'query':barcode
        }

        var result = 0

        $.ajax({
            url:$('#search_url').val(),
            data:form_data,
            'async': false,
            'type': "GET",
            'global': false,
            'dataType': 'html',
            success: function (response){
                result = response
            }
        })

        return result

    }

    Stock(pk)
    {

        let stock = JSON.parse(api_call('products','get_stock',{'pk':pk}))

        console.table(stock['message'])

        let tr = ''

        for (let i = 0; i < stock['message'].length; i++) {
            let row = stock['message'][i]

            tr += `<tr><td>${row['loc']}</td><td>${row['loc_descr']}</td><td>${row['stock']}</td></tr>`

        }

        let thd = `<table class="table table-sm table-info"><thead><tr><th>CODE</th><th>LOCATION</th><th>STOCK</th></tr></thead>`
        let tbd = `<tbody>${tr}</tbody></table>`
        $('#g_modal_title').text('STOCK REPORT')
        $('#g_modal_body').html(thd + tbd)
        $('#g_modal').modal('show')

    }

}