$(function() {
    //hang on event of form with id=myform
    $("#general_form").submit(function(e) {
//prevent Default functionality

        if($('#body').val().length < 1)
        {
            $("#general_form").submit()
        } else
        {
            e.preventDefault();
            //get the action-url of the form
            var actionurl = e.currentTarget.action;

            //$("#loader").modal("show");
            let formData = new FormData($(this).parents('form')[0]);

            formData = new FormData($('#general_form')[0]); // The form with the file inputs.
            const that = $(this),
                url = that.attr('action'),
                type = that.attr('method'),
                data = {};
            //console.log(url)

            that.find('[name]').each(function (index,value){
                var that = $(this), name = that.attr('name');
                data[name] = that.val();
            });

            $.ajax({

                url: url,
                type: type,
                data: formData,
                processData: false,  // tell jQuery not to process the data
                contentType: false,  // tell jQuery not to set contentType
                success: function (response){
                    error_handler(response)
                    console.table(response)
                },

            });

            return false;
        }



    });

});
