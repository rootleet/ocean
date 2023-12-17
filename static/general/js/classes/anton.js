class Anton {

    // calculate xyz
    lineXyz(line){
        let x = $(`#x_${line}`).val()
        let y = $(`#y_${line}`).val()
        let z = parseFloat(x*y).toFixed(2)
        console.log(x)
        $(`#z_${line}`).val(z)
    }

    validateInputs(ids) {
        for (let i = 0; i < ids.length; i++) {
            const value = $(`#${ids[i]}`).val();
            if (value === '' || value === undefined) {
                // alert('False');
                return false;
                $(`#${ids[i]}`).addClass('border-danger')
                $(`#${ids[i]}`).removeClass('border-success')
            } else {
                $(`#${ids[i]}`).addClass('border-success')
                $(`#${ids[i]}`).removeClass('border-danger')
            }
        }
        return true;
    }

    Inputs(ids){
        let xd = {};
        for (let i = 0; i < ids.length; i++) {
            xd[ids[i]] = $(`#${ids[i]}`).val()
        }

        return xd;
    }

    wait(time = 1){
        setTimeout(function () {
            console.log(waiting)
        },time * 1000)
    }


    Users(){
        let payload = {
            'module':'users',
            data : {}
        }

        return api.call('VIEW', payload, '/apiv2/')
    }

    IsRequest(request) {
        if(request['status_code'] === 200){
            return true
        }
        return false;

    }




}

class LineCalculate {
    #calculate(line, operator) {
        const x = Number($(`#x_${line}`).val());
        const y = Number($(`#y_${line}`).val());
        let z;

        switch(operator) {
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
    write(line){
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

  set_message(message){
      let payload = {
          'module':'tools',
          'data':{
              'task':'set_message',
              'message':message
          }
      }

      api.call('PUT',payload,'/adapi/')
  }

  html(message){
      Swal.fire({
            html: message,
            customClass: {
                content: 'text-left'
            }
        });

  }

  confirm(message,reload=0,to='/'){
       Swal.fire({
        title: 'Confirmation',
        text: message,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        reverseButtons: true, // To swap the positions of "Cancel" and "OK" buttons
      }).then((result) => {
        // Check if the user clicked "OK"
        if (result.isConfirmed) {
          if(reload === 1){
              if(to==='here'){
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
        if(response['status_code'] === 200){
            kasa.success("PASS")
        } else {
            kasa.error(response['message'])
        }
    }
}

class reportCard {
    setBody(data){
        $('#reportCardBody').html(data)
    }

    setTitle(title){
        $('#reportCardTitle').html(title)
    }

    setTitleHtml(html){
        $('#reportCardTitle').html(html)
    }
    getBody(){
        return $('#reportCardBody').html()
    }
    setFooter(footer){
        $('#reportCardFooter').html(footer)
    }
}

class ReportCard {
    export(doc,key,format){
        let payload = {
            'module':'',
            'data':{
                doc:doc,
                key:key,
                output:format
            }
        }
        return  api.call('POST',payload,'/reports/api/')

    }

    download(doc,key,format){
        kasa.html(`<a target="_blank" href="/${rops.export(doc,key,format)['message']}">DOWNLOAD</a>`)
    }

}

class Loader {
    show(){
        $('#loader').show()
    }

    hide(){
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