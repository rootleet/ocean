// car jobs trigger
$(document).ready(function() { // wait for the document to finish loading
  $("#carJob").click(function() {
      // $('#loader').modal('show')
      let carno = $('#searchQuery').val()
        $('#custBody').html('')
          $('#assetBody').html('')
          $('#tbody').html('')
      if(carno.length > 0){
          cmms.carJob(carno)
      } else {
          al('error','Please provide car numbeer')
      }
    $('#loader').delay(3000).modal('hide')
  });

  // get follow-ups
  $('#carFollups').click(function () {
    let carno = $('#searchQuery').val()

      if(carno.length > 0){
          let follows = cmms.carFollowUps(carno)
          if(isJson(follows)){
            let fols = JSON.parse(follows)
              let status = fols['status']
              if(status === 200){
                  let message = fols['message']
                  if(message['count'] > 0 ){
                      let records = message['records']
                      let ftr = ''
                      for (let r = 0; r < records.length; r++) {
                            let record = records[r]
                            ftr += `<tr>
                                        <td>${record['owner']}</td>
                                        <td>${record['created_date']} ${record['created_time']}</td>
                                        <td>${record['title']}</td>
                                        <td><i class="fa fa-reply pointer" onclick="al('info','${record['message']}')"></i></td>
                                    </tr>`
                      }
                      $('#fTbody').html(ftr)
                      $('#followUps').modal('show')
                  }
              } else {
                  al('error',fols['message'])
              }
          } else {
              al('error',"Follow up response cannot be displayed")
          }
      } else {
          al('error','Please provide car numbeer')
      }
  });
});

