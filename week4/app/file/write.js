$(document).ready(function(){
    $('#detail_summernote').summernote({
        placeholder:'작은 내용',
        tabsize:2,
        height: 300,
        toolbar: [
            ['fontsize', ['fontsize']],
            ['fontname', ['fontname']],
            ['font', ['bold', 'underline','strikethrough']],
            ['para', ['paragraph']],
            ['color', ['color']],
            ['insert', ['picture', 'video', 'link']],
        ],
        callbacks:{
            onImageUpload: function(files) {
                if (files.length > 0) {
                    let file = files[0];
                    let formData = new FormData();
                    formData.append('file', file);

                    $.ajax({
                        url:'/insertImage',
                        method: 'POST',
                        data: formData,
                        contentType: false,
                        processData: false,
                        success: function(response) {
                            if (response.url){
                                $('#detail_summernote').summernote('insertImage', response.url);
                            }
                        },
                        error: function(error) {
                            console.log("이미지 업로드 에러 : ", error);
                        }
                    });
                }
            },

            onVideoUpload: function() {
            let url = prompt("YouTube 동영상 URL 주소를 입력하세요");
            if (url) {
                let videoId = extractYouTubeID(url);
                if (videoId) {
                    let embedUrl = `https://www.youtube.com/embed/${videoId}`;
                    let iframeTag = `<iframe width='560' height='315' src="${embedUrl}" frameborder="0"></iframe>`;
                    $('#detail_summernote').summernote('insertVideo', embedUrl);  // insertVideo 함수 사용
                } else {
                    alert('올바른 YouTube URL을 입력하세요.');
                }
            }
        }
    }
});

    // Youtube url 추출
    function extractYouTubeID(url) {
        const regExp = /^.*(youtu.be\/|v\/|embed\/watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length == 11) ? match[2] : null;
    }

    $('#big_summernote').summernote({
        airMode:true

    });

    $('form').on('submit', function() {
        $('#bigcontent').val($('#big_summernote').summernote('code'));
        $('#detailcontent').val($('#detail_summernote').summernote('code'));

    });

});