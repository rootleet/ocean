class Blog {
    saveArticle(){
        let ids = ['title','tags','mypk'];
        let content = tinymce.get('article_desc').getContent();
        if(anton.validateInputs(ids) && content.length > 0){

            let payload = api.payload
            payload['module'] = 'new_article';
            payload['data'] = anton.Inputs(ids);
            payload['data']['content']= content
            payload['data']['owner'] = $('#mypk').val()

            let response = api.call('PUT',payload,'/blog/api/')
            kasa.response(response)

        } else {
            kasa.error("Please Fill All Fields");
        }
    }
}

const blog = new Blog()