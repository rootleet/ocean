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
        $('#g_modal_title').text(title)
    }

    setFooterHtml(html){
        $('#g_footer').html(html)
    }

    show(){
        $('#g_modal').modal('show')
    }
    hide(){
        $('#g_modal').modal('hide')
    }

}

const amodal = new Modal()