class Form {
    input(type='text',ini,comment = '',required=false){
        let req = ''
        if(required){
            req = `<span class="text-danger">*</span>`
        }
        return `
                <div class="input-group mb-2">
                <label class="w-100" for="${ini}">${ini.toUpperCase()} ${req}</label>
                <input type="${type}" id="${ini}" name="${ini}" required="${required}" class="form-control w-100 rounded-0"  />
                <small class="text-info">${comment}</small>
                </div>
                `
    }
    text(ini,comment='',required=false){
        return this.input('text',ini,comment,required)
    }

    email(ini,comment='',required=false){
        return this.input('email',ini,comment,required)
    }

    phone(ini,comment='',required=false){
        return this.input('tel',ini,comment,required)
    }

    date(ini,comment='',required=false){
        return this.input('date',ini,comment,required)
    }

    date_local(ini,comment='',required=false){
        return this.input('datetime-local',ini,comment,required)
    }

    time(ini,comment='',required=false){
        return this.input('time',ini,comment,required)
    }

    select(ini,options,comment='',required=false){
        let req = ''
        if(required){
            req = `<span class="text-danger">*</span>`
        }
        return `
                <label for="${ini}">${ini.toUpperCase()} ${req}</label>
                <select id="${ini}" name="${ini}" required="${required}" class="form-control mb-2 rounded-0"><${options}</select>
                `
    }

    button(ini,type){
        return `<button class="btn btn-info" id="${ini}" type="${type}">${ini.toUpperCase()}</button>`
    }
    textarea(ini,rows=3,required=false){
        let req = ''
        if(required){
            req = `<span class="text-danger">*</span>`
        }
        return `
                <label for="${ini}">${ini.toUpperCase()} ${req}</label>
                <textarea id="${ini}" name="${ini}" required="${required}" class="form-control mb-2 rounded-0" rows="${rows}"></textarea>
                `
    }

    file(ini,comment='',required=false){
        return this.input('file',ini,comment,required)
    }
}

const fom = new Form()