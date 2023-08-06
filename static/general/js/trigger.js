// car jobs trigger
$(document).ready(function () { // wait for the document to finish loading
    $('#carFollups').hide()
    $("#carJob").click(function () {
        // $('#loader').modal('show')
        let carno = $('#searchQuery').val()
        $('#custBody').html('')
        $('#assetBody').html('')
        $('#tbody').html('')
        if (carno.length > 0) {
            cmms.carJob(carno)
        } else {
            al('error', 'Please provide car numbeer')
        }
        $('#loader').delay(3000).modal('hide')
    });



    // get follow-ups
    $('#carFollups').click(function () {
        let carno = $('#searchQuery').val()

        if (carno.length > 0) {
            let follows = cmms.carFollowUps(carno)
            if (isJson(follows)) {
                let fols = JSON.parse(follows)
                let status = fols['status']
                if (status === 200) {
                    let ftr = ''
                    let message = fols['message']

                    if (message['count'] > 0) {
                        let records = message['records']

                        for (let r = 0; r < records.length; r++) {
                            let record = records[r]
                            ftr += `<tr>
                                        <td>${record['owner']}</td>
                                        <td>${record['created_date']} ${record['created_time']}</td>
                                        <td>${record['title']}</td>
                                        <td><i class="fa fa-reply pointer" onclick="al('info','${record['message']}')"></i></td>
                                    </tr>`
                        }


                    }
                    $('#fTbody').html(ftr)
                    $('#followUps').modal('show')
                } else {
                    al('error', fols['message'])
                }
            } else {
                al('error', "Follow up response cannot be displayed")
            }
        } else {
            al('error', 'Please provide car numbeer')
        }
    });

    // new follow up message
    $('#newFolloupButton').click(function () {
        let carno = $('#searchQuery').val()
        if (carno.length > 0) {
            $('newFolloup').modal('show')
        }
    });

    //cmms stock add
    $('#stockFind').click(function () {
        cmms.stockFind()
        // let barcode = $('#stock_add_barcode').val()

        // // validate barcode
        // if(barcode.length > 0 ){
        //     // get item details
        //     let payload = {
        //         "module":"product",
        //         "data":{
        //           "range":"single",
        //           "barcode":barcode
        //         }
        //     }

        //     // api call
        //     let response = api.call('VIEW',payload,'/cmms/api/')
        //     let status,status_code,message

        //     status = response['status']
        //     status_code = response['status_code']
        //     message = response['message']

        //     if(status_code === 200){
        //         let count,trans 
        //         count = message['count']
                
        //         // there is positive resposne
        //         if(count === 1){
        //             // there is product as expected
        //             trans = message['trans'][0]
        //             let name,item_ref
        //             name = trans['name']
        //             item_ref = trans['item_ref']
                    
        //             // add item
        //             Swal.fire({
        //                 'title':'STOCK RECORD',
        //                 'html':`<div style='text-align:left'><strong>BARCODE</strong> : <small class='text-info'>${barcode}</small><br><strong>NAME</strong> : <small class='text-info'>${name}</small></div>
        //                 <hr><input id='item_ref' value='${item_ref}' class='form-control mb-2' readonly>
        //                 <input min='1' id='take_qty' class='form-control mb-2' type='number'>
        //                 <button onclick='cmms.stockCount()' class='btn btn-success w-100'>ADD</button>`
        //             });

        //             // let tr = `<tr><td><small>${barcode}</small></td><td><small>${name}</small></td><td><small>10</small></td></tr>`

        //             // $('#tbody').prepend(tr)
                    
        //         } else {
        //             alert(`NO PRODUCT FOUND (${count})`)
        //         }
        //     } else {
        //         alert(message)
        //     }

            
        // } else {
        //     alert("BARCODE SHOULD ENTER")
        // }
    })

    // cmms input 
    $('#stock_add_barcode').keypress(function(event) {
        // Check if Enter key is pressed (keycode 13)
        if (event.which === 13) {
          cmms.stockFind()
        }
      });

    // infographic
    $('#infographic').click(function () {
        $('#more').modal('show');
        maximizeBrowserWindow();
        setTimeout(exitFullscreen, 3000);
    });

});

