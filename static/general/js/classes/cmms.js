class Cmms {
    carMaintainanceLog(carNumber){

        let data = {
            "menu": {
                "header":"carjob",
                "data":{
                    "carno":carNumber,
                    "records":5
                }
            }
        }
        return apiv2('cmms','null',data)

    }

    carJob(carNumber){

        let response = cmms.carMaintainanceLog(carNumber)
        if(isJson(response)){
            let resp = JSON.parse(response);
            let status,message
            status = resp['status']

            if(status === 200){
                // positive response
                message = resp['message']

                let customer,asset,wos,woc
                customer = message['customer']
                asset = message['asset'];
                wos = message['jobs']
                woc = wos['count']

                // load header
                let car_detail = `<table class="table-sm">
                                <tr>
                                    <td>Name : </td><td>${asset['name']}</td>
                                </tr>
                                <tr>
                                    <td>Car N<u>0</u> : </td><td>${asset['asset_no']}</td>
                                </tr>
                                <tr>
                                    <td>Chassis : </td><td>${asset['chassis']}</td>
                                </tr>
                            </table>`
                $('#assetBody').html(car_detail)

                let cust_detail = `<table class="table-sm">
                                <tr>
                                    <td>Name : </td><td>${customer['name']}</td>
                                </tr>
                                <tr>
                                    <td>Contact : </td><td>${customer['contact']}</td>
                                </tr>
                            </table>`
                $('#custBody').html(cust_detail)

                // al('success',"LOAD HEADER")

                let wotr = ''
                if(woc > 0){
                    // load trans

                    let wor = wos['records']
                    for (let w = 0; w < wor.length; w++) {
                        let wo = wor[w]
                        wotr += `<tr>
                                <td>${wo['wreq_no']}</td>
                                <td>${wo['wo_no']}</td>
                                <td>${wo['invoice_entry']}</td>
                                <td>${wo['wo_date']}</td>
                            </tr>`
                    }
                } else{
                    wotr = "NO WO TRANS"
                }
                $('#tbody').html(wotr)
                $('#carFollups').show()


            } else {
                al('info',resp['message'])
            }

            ctable(resp)
        } else {
            swal_response("There is an error retrieving car job")
        }

    }

    carFollowUps(carNumber){
        let data = {
            "menu": {
                "header":"followup",
                "data":{
                    "carno":carNumber,
                    "records":5
                }
            }
        }

        return apiv2('cmms','none',data)
    }

    SaveFollowup(){
        let carno = $('#searchQuery').val()
        if(carno.length > 0){
            let title, message
            title = $('#ftitle').val();
            message = $('#freply').val();

            if(title.length < 1){
                al('error',"Please provide feedback title")
            } else if (message.length < 1)
            {
                al('error',"Please provide feedback response")
            } else {

                // save
                let data = {
                    "menu": {
                        "header":"newfollowup",
                        "data":{
                            "carno":carno,
                            "title":title,
                            "message":message,
                            "owner":1
                        }
                    }
                }

                apiv2('cmms','null',data)
                cmms.carFollowUps(carno)
                $('#newFolloup').modal('hide')
                al('success',"Response logged")

            }



        }
    }

}

const cmms = new Cmms()