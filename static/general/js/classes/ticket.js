class Ticket {
    newTicket(){
        // let title = $('#title').val()
        // let description = $('#description').val()
        // let owner = 1

        var owner = $('#owner').val().trim();
          var title = $('#title').val().trim();
          var description = $('#description').val().trim();

      if (owner === '' || title === '' || description === '') {
        alert('Please fill in all the fields');
      } else {
        let data = {
            "module":"ticket",
            "data":{
                "owner":owner,
                "title":title,
                "descr":description
            }
        }

        let call = api.put(data)

        if(isJson(JSON.stringify(call))){

            let resp = call

            alert(resp['message'])

            // location.reload()

        } else {
            al('error',"Unexpected Response")
        }
      }



    }
}

const ticket = new Ticket();