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

    updateTranScreen(){
        let form = `
            <label for="title">TITLE</label><input type="text" id="title" class="form-control rounded-0 mb-2" placeholder="" />
            <label for="description">DESCRIPTION</label><textarea name="" id="description" cols="30" rows="5" class="form-control rounded-0 mb-2" placeholder=""></textarea>
            <label for="datetime">DATE TIME</label><input type="datetime-local" name="" class="form-control rounded-0 mb-2" id="datetime">
           
            <label for="notify">NOTIFY</label><select name="notify" class="form-control rounded-0 mb-2" id="notify">
                <option value="NO">NO</option>
                <option value="YES">YES</option>
            </select>
            <button onclick="ticket.saveTicketTran()" class="btn btn-sm btn-success w-100">SUBMIT</button>
            
        `;
        amodal.setBodyHtml(form);
        amodal.setTitleText("UPDATE TICKET");
        amodal.show()
    }

    saveTicketTran(){
        let inputs = ['title','description','datetime','cardno','mypk'];

        if(anton.validateInputs(inputs)){
            let jobcard = api.call('VIEW',{module:'servicecard',data:{cardno:$('#cardno').val()}},'/servicing/api/');
            if(jobcard['status_code'] === 200){
                let payload = {
                    module:'ticketupdate',
                    data:anton.Inputs(inputs)
                }
                console.table(jobcard)
                payload['data']['ticket'] = jobcard['message']['ticket']['hd']['pk']


                amodal.hide();

                let request = api.call('PUT',payload,'/adapi/');

                kasa.info(request['message']);
                loadJobCard(payload['data']['cardno'])
            } else {
                kasa.error(jobcard['message']);
            }


        } else {
            kasa.error("INVALID FORM")
        }

        amodal.hide();
    }

    sendToClient(cardno){
        Swal.fire({
          title: 'MESSAGE',
          html:
            '<textarea id="message" class="form-control rounded-0" rows="5" placeholder="Text"></textarea>',
          showCancelButton: true,
          confirmButtonText: 'Confirm',
          cancelButtonText: 'Cancel',
          showLoaderOnConfirm: true,
          preConfirm: () => {
            const message = document.getElementById('message').value;

            // You can use textInputValue and textareaInputValue as needed
            let payload = {
                module:'send_ticket_to_client',
                data: {
                    cardno:cardno,
                    message:message
                }
            }

            kasa.info(api.call('PUT',payload,'/servicing/api/')['message']);
            loadJobCard(cardno)

          }
        });

    }

    approveTicket(cardno,status){
        Swal.fire({
          title: 'ENTER FEED BACK',
          html:
            '<textarea id="message" class="form-control rounded-0" rows="5" placeholder="Text"></textarea>',
          showCancelButton: true,
          confirmButtonText: 'Confirm',
          cancelButtonText: 'Cancel',
          showLoaderOnConfirm: true,
          preConfirm: () => {
            const message = document.getElementById('message').value;

            // You can use textInputValue and textareaInputValue as needed
            let payload = {
                module:'client_ticket_approval',
                data: {
                    cardno:cardno,
                    message:message,
                    status:status
                }
            }

            kasa.confirm(api.call('PATCH',payload,'/servicing/api/')['message'],1,'here')

          }
        });
    }


}

const ticket = new Ticket();