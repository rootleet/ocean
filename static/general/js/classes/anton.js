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
            const value = $(`#${ids[i]}`).val().trim();
            if (value === '') {
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

  html(message){
      Swal.fire({
          html:message
      })
  }

}


const linecomment = new LineComment()
const kasa = new Kasa()
const anton = new Anton();
const lincal = new LineCalculate()