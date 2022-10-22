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


}