var swiper = new Swiper('.swiper-container', {
    pagination: '.swiper-pagination',
    paginationClickable: true,
    loop: true,
    autoplay: 3000,


    speed: 1000,
    prevButton: '.swiper-button-prev',
    nextButton: '.swiper-button-next',
    effect: 'slide',//  effect: 'flip',effect: 'coverflow',slide', 'fade',cube,
    grabCursor: true,
    cube: {
        shadow: false,
        slideShadows: false,
        shadowOffset: 20,
        shadowScale: 0.94
    }
});

// 点击显示登录控件
$(function () {
    $('#index_login').click(function () {
        $('.mypop').show();
    });
    $('.close,#cancel').click(function () {
        $('.mypop').hide();
    })
});

// 弹出登录对话框，进行登录
$('button#index_login').click(function () {
    var username = $('#login_username').val();
    var password = $('#login_password').val();
    if (username === '' || password === '' ) {
        $('#message').text("手机号或密码不能为空")
    }else if(username.length<11){
        $('#message').text("帐号或密码错误")
    }
    else {
        $.ajax({
            // user.py  blueprint  加了url_prefix 所以地址从/user开始
            url: $SCRIPT_ROOT + "/user/index_login",
            type: 'post',
            data: {username: username, password: password},
            dataType: 'json',
            // async: false,
            success: function (data) {
                //登录失败
                if (data.result === 'False') {
                    $('#message').text(data.error)
                } else if (data.result === 'True') {
                    window.location.reload()
                }
            },
            error: function (e) {
                alert('index_login error:' + e)
            },
        })
    }
});
