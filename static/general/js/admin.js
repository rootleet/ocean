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

async function close_issue(issue_id) {
    let url = $('#close_url').val()



    const {value: text} = await Swal.fire({
        input: 'textarea',
        inputLabel: 'Closing Remarks',
        inputPlaceholder: 'Type your message here...',
        inputAttributes: {
            'aria-label': 'Type your message here'
        },
        showCancelButton: true
    })

    if (text) {
        let form_data = {
        'entry': issue_id,'remarks':text
    }
        $.ajax({
                url: url,
                data: form_data,
                type: "GET",
                success: function (response) {
                    error_handler(response)
                }
            })

    }




}


async function task_export(document) {
    const {value: doc_type} = await Swal.fire({
        title: 'Select field validation',
        input: 'select',
        inputOptions: {
            'csv': 'CSV'
        },

        inputPlaceholder: 'Document Type',
        showCancelButton: true,
        // inputValidator: (value) => {
        //     return new Promise((resolve) => {
        //         if (value === 'oranges') {
        //             resolve()
        //         } else {
        //             resolve('You need to select oranges :)')
        //         }
        //     })
        // }
    })

    if (doc_type) {
        const inputOptions = new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              '0': 'Open',
              '1': 'Closed',
              '*': 'All'
            })
          }, 1000)
        })

        const { value: sort } = await Swal.fire({
          title: 'Select Sort',
          input: 'radio',
          inputOptions: inputOptions,
          inputValidator: (value) => {
            if (!value) {
              return 'You need to choose something!'
            }
          }
        })

        if (sort) {
            let url = $('#export_url').val();
            var form_date = {
                'sort':sort,
                'doc_type':doc_type
            }
            $.ajax({
                url:url,
                data:form_date,
                type:'GET',
                success: function (response) {
                    error_handler(response)
                    console.log(response)
                }
            })
          Swal.fire({ html: `You selected: ${sort} Doc : ${doc_type}` })
        }
    }
}


$(function() {
    $("#search_task").on("change paste keyup", function() {
       let query = $(this).val()

        let form_date = {
           'for':'task',
            'query':query
        }

        if(query.length > 0)
        {
            $.ajax({
            url:$('#search_url').val(),
            data:form_date,
            type: 'GET',
            success: function (response) {
                console.log(response)
                let res = response
                let this_row;
                let link_res = ""
                for (let i = 0; i < res.length; i++) {
                    this_row = res[i]['fields']
                    link_res += `<a href="/admin_panel/view_task/${this_row.entry_uni}/" class="list-group-item">${this_row.title}</a>`
                }
                $('#searchRes').html(link_res)
            }
        })
        } else {
            $('#searchRes').html('')
        }


    });
});;