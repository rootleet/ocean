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

function mark_for_escalation(issue) {

    let url = $('#url').val()
    let form_date = {
        'issue':issue
    }
    $.ajax({
            url:url,
            type:'GET',
            data:form_date,
            success: function (response) {
                error_handler(response)
                console.log(response)
            }
        })
}

async function escalate(provider_code) {
    const {value: text} = await Swal.fire({
        input: 'textarea',
        inputLabel: 'Message',
        inputPlaceholder: 'Type your message here...',
        inputAttributes: {
            'aria-label': 'Type your message here'
        },
        showCancelButton: true
    })

    if (text) {
        var form_date = {
        'x_provider':provider_code,
            'email':$('#Email').html(),
            'subject':text
        }
        var url = $('#send_url').val()
        $.ajax({
            url:url,
            type:'GET',
            data:form_date,
            success: function (response) {
                swal_success(response)
            }
        })
        //Swal.fire(text)

    } else {
        await escalate(provider_code)
    }
}