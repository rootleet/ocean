class Modal {
    setSize(size='L'){
      let sizeClasses = {
        'L': 'modal-lg',
        'XL': 'modal-xl'
      };
      let sizeClass = sizeClasses[size];

      if(sizeClass){
        // Remove all other size classes
        Object.values(sizeClasses).forEach(c => {
          $('#g_modal_size').removeClass(c);
        });

        // Add the class for the current size
        $('#g_modal_size').addClass(sizeClass);
      }
    }

    position(P){
        let posClass = {
            'C':'modal-dialog-centered'
        }
        let pos = posClass[P]
        if(pos){
            $('#g_modal_size').addClass(pos)
        }
    }

    setBodyHtml(html){
        $('#g_modal_body').html(html)
    }

    setTitleText(title){
        let close = `<button data-bs-dismiss='modal' class='close'>&times;</button>`;
        let title_html = `
        <div class='w-100 d-flex flex-wrap'>
            <div class='w-75'>${title}</div>
            <div class='w-25 d-flex flex-wrap justify-content-end'>${close}</div>
        </div>
         
        `
        $('#g_modal_title').html(title)
    }

    setFooterHtml(html){
        $('#g_footer').html(html)
    }

    show(){
        $('#g_modal').modal('show')
    }
    hide(clear=true){
        if(clear === true){
            this.setTitleText('');
            this.setFooterHtml('');
            this.setBodyHtml('');
        }
        $('#g_modal').modal('hide')
    }

}

const amodal = new Modal()
const pop = new Modal()