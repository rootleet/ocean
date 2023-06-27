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

            location.reload()

        } else {
            al('error',"Unexpected Response")
        }
      }



    }

    updateTask(){
        let title,details,update_time,support_by,owner,data,task

        task = $('#task').val()
        title = $('#title').val()
        details = $('#details').val()
        update_time = $('#time').val()
        support_by = $('#supp_by').val()
        owner = $('#pk').val();

        data = {
            'module':'task',
            'do':'update',
            'data':{
                'task':task,'title':title,'detail':details,'date':update_time,'support_by':support_by,'owner':owner
            }
        }

        let save = api.put(data)

        location.reload()
        al('info',save['message'])


    }

}

const ticket = new Ticket();