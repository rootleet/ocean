var currentDate = new Date()
var day = currentDate.getDate()
var month = currentDate.getMonth() + 1
var year = currentDate.getFullYear()

// Function to get today's date in yyyy-mm-dd format
function getTodayDate() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Example usage
const todayDate = getTodayDate();
const today = todayDate


$(function() {
    //hang on event of form with id=myform
    $("#general_form").submit(function(e) {
//prevent Default functionality
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
        console.log(url)

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

                console.log(response)
                error_handler(response)

            },

        });

        return false;

    });

});



function visibility_show(id)
{
    if(document.getElementById(id))
    {
        document.getElementById(id).style.visibility= 'visible';
        console.log('show')
    }
}
function visibility_hide(id)
{
    if(document.getElementById(id))
    {
        document.getElementById(id).style.visibility= 'hidden';
        console.log('hide')
    }
}



function set_session(data)
{
    var form_data = {
        'function':'set_session',
        'session_data':data
    }
    $.ajax({
        url: '/admin/backend/process/form.php',
        type: 'POST',
        data: form_data,
        success: function (response) {
            location.reload();
        }
    });

    return false;
}

function reload()
{
    location.reload();
}

function delete_event(event)
{
    $('#loader').model('show');
}

$(function() {
    //hang on event of form with id=myform
    $("#text_form").submit(function(e) {

        var loading = "<button class=\"btn btn-primary w-100 h-100\" disabled>\n" +
            "  <span class=\"spinner-grow spinner-grow-sm\"></span>\n" +
            "  Processing Request..\n" +
            "</button>";

        //prevent Default functionality
        e.preventDefault();

        //get the action-url of the form
        var actionurl = e.currentTarget.action;
        var formData = $("#text_form").serialize();
        // console.log(actionurl)

        //do your own request an handle the results
        console.log('ajax ahead');
        $('#text_form').html(loading);
        $.ajax({
            url: actionurl,
            type: 'POST',
            data: formData,
            success: function (response)
            {

                console.log(response);

                // split response
                var response_type = response.split('%%');
                //console.log(response_type.length)
                if(response_type.length > 1)
                {
                    var action = response_type[0];
                    var message = response_type[1];
                    // console.log(action)
                    switch (action) {
                        case 'done':
                            // reload
                            reload();
                            break;
                        case 'book':
                            var sh = "<div class='alert alert-success text-center p-5 m-0'>" +
                                "<strong class='m-0'>Booking Successful</strong>" +
                                "<p class='m-0'>Our response team will contact you soon</p>" +
                                "</div>";
                            $('#text_form').html(sh);
                            $('#text_form').addClass('p-0 m-0');
                            setTimeout(function(){
                                $('#book').modal('hide');
                            }, 3000)
                            break;
                        case 'book_err':
                            var sh = "<div class='alert alert-danger text-center p-5 m-0'>" +
                                "<strong class='m-0'>System Busy</strong>" +
                                "<p class='m-0'>Sorry your request can't be processed now, please contact out office for suppurt</p>" +
                                "</div>";
                            $('#text_form').html(sh);
                            $('#text_form').addClass('p-0 m-0');
                            setTimeout(function(){
                                $('#book').modal('hide');
                            }, 5000)
                            break;
                        case 'err':
                            $('#form_err').text(message.toString());
                            // show error
                            break;
                        default:
                            reload()
                            // reload
                    }
                }

            }
        });

    });

});



// upload file
$(function() {
    //hang on event of form with id=myform
    $("#upload_file_form").submit(function(e) {


        $("#loader").modal("show");

        //prevent Default functionality
        e.preventDefault();
        //get the action-url of the form
        var actionurl = e.currentTarget.action;
        var formData = new FormData($(this).parents('form')[0]);

        var formData = new FormData($('#upload_file_form')[0]); // The form with the file inputs.
        var that = $(this),
            url = that.attr('action'),
            type = that.attr('method'),
            data = {};
         console.log(url)

        that.find('[name]').each(function (index,value){
            var that = $(this),
                name = that.attr('name'),
                value = that.val();
            data[name] = value;
        });

        $.ajax({

            xhr: function() {
                var progress = $('.progress'),
                    xhr = $.ajaxSettings.xhr();

                progress.show();

                xhr.upload.onprogress = function(ev) {
                    if (ev.lengthComputable) {
                        var percentComplete = parseInt((ev.loaded / ev.total) * 100);
                        progress.val(percentComplete);
                        if (percentComplete === 100) {
                            progress.hide().val(0);
                        }
                    }
                };

                return xhr;
            },

            url: url,
            type: type,
            data: formData,
            processData: false,  // tell jQuery not to process the data
            contentType: false,  // tell jQuery not to set contentType
            success: function (response){
                console.log('ajax made');
                $('msg').text(response);
                console.log(response);

                // split response
                var response_type = response.split('%%');
                //console.log(response_type.length)
                if(response_type.length > 1)
                {
                    var action = response_type[0];
                    var message = response_type[1];
                    // console.log(action)
                    switch (action) {
                        case 'done':
                            // reload
                            $('#form_succ').text('Process complete');
                            setTimeout(function(){
                                location.reload();
                            }, 5000);
                            break;
                        case 'err':
                            $('#form_err').text('There is an issue with your process, contact us for help');
                            setTimeout(function(){
                                location.reload();
                            }, 5000);
                            // show error
                            break;
                        default:
                            reload()
                        // reload
                    }
                }
            },

        });

        return false;

    });

});

// make book
function book(package)
{
    document.getElementById('booking_package').value = package;

    // show modal
    $('#book').modal('show');
}

function load_convo_message() {
    let pk = $('#article_pk').val()
    let ini_count = $('#messages div').length
    var form_date = {
        'article_pk':pk
    }

    $.ajax({
        url: $('#load_convo_url').val(),
        type: 'GET',
        data: form_date,
        success: function (response) {
            // error_handler(response)
            console.log(response)

            var d = $('#messages');
            d.html(response)
            let now_count = $('#messages div').length
            if(ini_count < now_count)
            {
                $('#new').show()
                // d.scrollTop(d.prop("scrollHeight"));
            }
            else
            {
                $('#new').hide()
            }


        }
    })
}


// Restore and maximize the browser window
// Maximize the browser window using Fullscreen API
function maximizeBrowserWindow() {
  var doc = window.document;
  var docEl = doc.documentElement;

  var requestFullScreen = docEl.requestFullscreen || docEl.mozRequestFullScreen || docEl.webkitRequestFullScreen || docEl.msRequestFullscreen;

  if (requestFullScreen) {
    requestFullScreen.call(docEl);
  }
}

function exitFullscreen() {
  var doc = window.document;

  var exitFullScreen = doc.exitFullscreen || doc.mozCancelFullScreen || doc.webkitExitFullscreen || doc.msExitFullscreen;

  if (exitFullScreen) {
    exitFullScreen.call(doc);
  }
}

//Creating dynamic link that automatically click
function downloadURI(uri, name) {
    var link = document.createElement("a");
    link.download = name;
    link.href = uri;
    link.click();
    //after creating link you should delete dynamic link
    //clearDynamicLink(link);
}

//Your modified code.
function printToFile(div) {
    html2canvas(div, {
        onrendered: function (canvas) {
            var myImage = canvas.toDataURL("image/png");
            //create your own dialog with warning before saving file
            //beforeDownloadReadMessage();
            //Then download file
            downloadURI("data:" + myImage, "yourImage.png");
        }
    });
}




