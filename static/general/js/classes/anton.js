class Anton {

    // calculate xyz
    lineXyz(line) {
        let x = $(`#x_${line}`).val()
        let y = $(`#y_${line}`).val()
        let z = parseFloat(x * y).toFixed(2)
        console.log(x)
        $(`#z_${line}`).val(z)
    }

    validateInputs(ids) {
        for (let i = 0; i < ids.length; i++) {
            let id_string = ids[i];
            const value = $(`#${ids[i]}`).val();
            console.log(`${id_string} = ${value}`);
            if (value === '' || value === undefined) {
                // alert('False');

                $(`#${ids[i]}`).addClass('border-danger')
                $(`#${ids[i]}`).removeClass('border-success')

                kasa.error(`Invalid Field ${id_string}`)
                return false;
            } else {
                $(`#${ids[i]}`).addClass('border-success')
                $(`#${ids[i]}`).removeClass('border-danger')
            }
        }
        return true;
    }

    Inputs(ids) {
        let xd = {};
        for (let i = 0; i < ids.length; i++) {
            xd[ids[i]] = $(`#${ids[i]}`).val()
        }

        return xd;
    }

    wait(time = 1) {
        setTimeout(function () {
            console.log(waiting)
        }, time * 1000)
    }


    Users() {
        let payload = {
            'module': 'users',
            data: {}
        }

        return api.call('VIEW', payload, '/apiv2/')
    }

    IsRequest(request) {
        if (request['status_code'] === 200 || request['status'] === 200) {
            return true
        }
        return false;

    }

    fileType(file) {
        let f_split = file.split('.')
        if (f_split.length > 0) {
            let ext = f_split[f_split.length - 1];
            switch (ext.toLowerCase()) {
                case 'png':
                    return 'image'
                    break;
                case 'jpeg':
                    return 'image'
                    break;
                case 'jpg':
                    return 'image'
                    break;
                case 'pdf':
                    return 'pdf'
                    break;
                case 'mp4':
                    return 'video';
                    break;

                default:
                    return `unknown : ${ext}`
                    break;
            }
        } else {
            return 'not_a_file'
        }
    }

    viewFile(url = '', title = null, description = null) {

        amodal.setTitleText("Error!!");
        amodal.setBodyHtml("Cannot Load Resource")
        if (url.length > 0) {
            amodal.setTitleText(title)
            let ft = this.fileType(url);
            if (ft === 'image') {
                amodal.setBodyHtml(
                    `<img class='img-fluid' src='${url}' />`
                );

            }

            else if (ft === 'pdf') {
                amodal.setBodyHtml(`<embed src="${url}" width="100%" height="600px" />`);
                amodal.setSize('XL')
            }

            else if (ft === 'video') {
                amodal.setBodyHtml(`
                <video width="100%" height="auto" controls>
                    <source src="${url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                `)
            }

            else {
                amodal.setTitleText("Consufe!!")
                amodal.setBodyHtml(`Cannot render resource type : ${ft} <br>Download file with link below <br> <a target='_blank' href='${url}'>>_Link_<</a>`)
            }
        }
        $('#g_modal_body').prepend(`<p>${description}</p>`)
        amodal.show()

    }

    printPDF(url) {
                
        var iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = url;
        document.body.appendChild(iframe);
        iframe.onload = function() {
            iframe.contentWindow.print();
        };
    }


    setValues(header = {}) {
        for (const headerKey in header) {
            $(`#${headerKey}`).val(header[headerKey])
        }

    }

    docNav(header = {}) {
        let next = header['next'];
        let previous = header['previous'];


        if(next === 0 || next === undefined){

            $('#next').prop('disabled',true)
            $('#next').val(undefined)
        } else {

            $('#next').prop('disabled',false)
            $('#next').val(next)
        }


        if(previous === 0 || previous === undefined){

            $('#previous').prop('disabled',true)
            $('#previous').val(undefined)
        } else {

            $('#previous').prop('disabled',false)
            $('#previous').val(next)
        }
    }
}

class LineCalculate {
    #calculate(line, operator) {
        const x = Number($(`#x_${line}`).val());
        const y = Number($(`#y_${line}`).val());
        let z;

        switch (operator) {
            case 'sub': z = x - y; break;
            case 'mul': z = x * y; break;
            case 'div': z = x / y; break;
            case 'add': z = x + y; break;
            default:
                console.error(`Invalid operator: ${operator}`);
                return;
        }

        $(`#z_${line}`).val(z.toFixed(2));
    }

    add(line) {
        this.#calculate(line, 'add');
    }

    sub(line) {
        this.#calculate(line, 'sub');
    }

    mul(line) {
        this.#calculate(line, 'mul');
    }

    div(line) {
        this.#calculate(line, 'div');
    }
}

class LineComment {
    write(line) {
        let name = $(`#name_${line}`).text()
        let already_comment = $(`#line${line}_comment`).val()
        Swal.fire({
            title: ``,
            html: `Enter Comment for ${name} <hr>
          
          <textarea id="comment-textarea" class="form-control" required placeholder="Enter your comment here...">${already_comment}</textarea>
        `,
            showCancelButton: true,
            confirmButtonText: 'Submit',
            preConfirm: () => {
                const comment = document.getElementById('comment-textarea').value;

                // Validate the input
                if (!comment) {
                    Swal.showValidationMessage('Please select a comment type and enter a comment');
                } else {

                    $(`#line${line}_comment`).val(comment)
                    kasa.success("Writing Comment....")

                }
            }
        });
    }
}

class Kasa {
    alert(icon, message) {

        Swal.fire({
            icon: icon,
            text: message,
            timer: 3000,
            showConfirmButton: false,
            timerProgressBar: true,
            allowOutsideClick: false,
            onBeforeOpen: () => {
                Swal.showLoading();
                var b = Swal.getHtmlContainer().querySelector('b');
                b.textContent = Swal.getTimerLeft();

                var timerInterval = setInterval(() => {
                    b.textContent = Swal.getTimerLeft();
                }, 100);

                Swal.stopTimer();
                setTimeout(() => {
                    Swal.resumeTimer();
                    Swal.hideLoading();
                    clearInterval(timerInterval);
                }, 100);
            }
        });
    }

    success(message) {
        this.alert('success', message);
    }

    error(message) {
        this.alert('error', message);
    }

    info(message) {
        this.alert('info', message);
    }

    warning(message) {
        this.alert('warning', message);
    }

    question(message) {
        this.alert('question', message);
    }

    set_message(message) {
        let payload = {
            'module': 'tools',
            'data': {
                'task': 'set_message',
                'message': message
            }
        }

        api.call('PUT', payload, '/adapi/')
    }

    html(message) {
        Swal.fire({
            html: message,
            customClass: {
                content: 'text-left'
            }
        });

    }

    confirm(message, reload = 0, to = '/') {
        Swal.fire({
            title: 'Confirmation',
            text: message,
            icon: 'question',
            showCancelButton: false,
            confirmButtonText: 'OK',
            reverseButtons: true, // To swap the positions of "Cancel" and "OK" buttons
        }).then((result) => {
            // Check if the user clicked "OK"
            if (result.isConfirmed) {
                if (reload === 1) {
                    if (to === 'here') {
                        location.reload()
                    } else {
                        location.href = to
                    }

                } else {
                    kasa.info('Thanks')
                }

            } else {
                Swal.fire('Cancelled', 'You cancelled the action', 'error');
            }
        });
    }

    response(response) {
        console.table(response)
        if (response['status_code'] === 200) {
            kasa.success(response['message'])
        } else {
            kasa.error(response['message'])
        }
    }
}

class reportCard {
    setBody(data) {
        $('#reportCardBody').html(data)
    }

    setTitle(title) {
        $('#reportCardTitle').html(title)
    }

    setTitleHtml(html) {
        $('#reportCardTitle').html(html)
    }
    getBody() {
        return $('#reportCardBody').html()
    }
    setFooter(footer) {
        $('#reportCardFooter').html(footer)
    }
}

class ReportCard {
    export(doc, key, format) {
        let payload = {
            'module': '',
            'data': {
                doc: doc,
                key: key,
                output: format
            }
        }
        return api.call('POST', payload, '/reports/api/')

    }

    download(doc, key, format) {
        kasa.html(`<a target="_blank" href="/${rops.export(doc, key, format)['message']}">DOWNLOAD</a>`)
    }

}

class Loader {
    show() {
        $('#loader').show()
    }

    hide() {
        $('#loader').hide()
    }
}

const loader = new Loader();
const rops = new ReportCard();
const card = new reportCard();
const linecomment = new LineComment();
const kasa = new Kasa();
const anton = new Anton();
const lincal = new LineCalculate()