function log_issue(uni) {
    let log_title = `#log_title_${uni}`
    let log_body = `#log_body_${uni}`
    let issues_url = $('#issues_url').val()
    let error = 0;

    if(!str_len($(log_title).val()) || !str_len($(log_body).val()) || !str_len(issues_url))
    {
        swal_response('error','Invalid Form','Please fill all required fields')
    } else
    {
        let form_date = {
            'issue':uni,
            'title':$(log_title).val(),
            'body': $(log_body).val()

        }

        $.ajax({
            url:issues_url,
            type:'GET',
            data:form_date,
            success: function (response) {
                error_handler(response)
            }
        })
    }


}