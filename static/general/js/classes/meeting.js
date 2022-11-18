class Meeting {
    NewMeetingTran(){
        let talking_point = $('#talking_point').val()
        let tran_text = $('#tran_text').val()
        let meeting = $('#meetingPk').val()

        if(talking_point !== 'null' && tran_text.length > 0)
        {
            let data = {
                'meeting':meeting,'talking_point':talking_point,'tran':tran_text
            }

            let apicall = api_call('meeting','tran',data)

            let jr = JSON.parse(apicall)
            console.table(jr)

            if(jr['status'] === 200)
            {
                this.liveTrans()
            }


        } else {

            error_handler('error%%Male Sure talking point is selected and also data is enterted')
        }


    }

    liveTrans(){
        let meeting = $('#meetingPk').val()
        let apicall = api_call('meeting','GrtTan',{'meeting':meeting})
        let jr = JSON.parse(apicall)


        if(jr['status'] === 200)
        {
            let m = jr['message']
            let ht = ""
            // console.table(m)
            for (let i = 0; i < m.length; i++) {
                let r = m[i]
                let point,descr,created_date,created_time,owner
                point = r['point']
                descr = r['descr']
                created_date = r['created_date']
                created_time = r['created_time']
                owner = r['owner']

                ht += `<div class="alert alert-primary">
                                                <strong>${point}</strong> <br>
                                                <p class="m-0">${descr}</p>
                                            </div>`

                console.table(r)
                console.log(point)
                $('#xBody').html(ht)
            }
        }

    }

    startMeeting() {
        if(confirm("Are you sure you want to start meeting"))
        {
            let apcall = api_call('meeting','start',{'meeting':$('#meetingPk').val()})
            let r = JSON.parse(apcall)

            if(r['status'] === 200)
            {
                location.reload()
            } else {
                error_handler('error%%Could Not Start Meeting')
            }
        }
    }

    endMeeting() {
        if(confirm("Are you sure you want to end meeting"))
        {
            let apcall = api_call('meeting','end',{'meeting':$('#meetingPk').val()})
            let r = JSON.parse(apcall)

            if(r['status'] === 200)
            {
                location.reload()
            } else {
                error_handler('error%%Could Not End Meeting')
            }
        }
    }
}

const meeting = new Meeting()