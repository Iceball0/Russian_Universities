$(document).ready(function(){
    // обрабатываем нажатия на кнопки меню, отображаем нужный блок и прячем остальные
    $(document.getElementsByName('info')[0]).click(function(){
        $('#info').css('display', 'block');
        $('#specialties').css('display', 'none');
        $('#universities').css('display', 'none');
        $('#news').css('display', 'none');
        $('#reviews').css('display', 'none');
        $('#location').css('display', 'none');
    });
    $(document.getElementsByName('specialties')[0]).click(function(){
        $('#info').css('display', 'none');
        $('#specialties').css('display', 'block');
        $('#news').css('display', 'none');
        $('#reviews').css('display', 'none');
        $('#location').css('display', 'none');
    });
    $(document.getElementsByName('universities')[0]).click(function(){
        $('#info').css('display', 'none');
        $('#universities').css('display', 'block');
    });
    $(document.getElementsByName('news')[0]).click(function(){
        $('#info').css('display', 'none');
        $('#specialties').css('display', 'none');
        $('#news').css('display', 'block');
        $('#reviews').css('display', 'none');
        $('#location').css('display', 'none');
    });
    $(document.getElementsByName('reviews')[0]).click(function(){
        $('#info').css('display', 'none');
        $('#specialties').css('display', 'none');
        $('#news').css('display', 'none');
        $('#reviews').css('display', 'block');
        $('#location').css('display', 'none');
    });
    $(document.getElementsByName('location')[0]).click(function(){
        $('#info').css('display', 'none');
        $('#specialties').css('display', 'none');
        $('#news').css('display', 'none');
        $('#reviews').css('display', 'none');
        $('#location').css('display', 'block');
    });
    $(document.getElementsByName('back')[0]).click(function(){
        window.location.href = '/';
    });
});