// // product 加减按钮
var num_jia = document.getElementById("add");
var num_jian = document.getElementById("cut");
var input_num = document.getElementById("num");
var stock = document.getElementById('stock');
num_jia.onclick = function () {
    if (input_num.value >= parseInt(stock.innerText)) {
        alert('没有这么多啦！库存不足了！')
    } else {
        input_num.value = parseInt(input_num.value) + 1;
    }
};
num_jian.onclick = function () {

    if (input_num.value <= 1) {
        input_num.value = 1;
    } else {
        input_num.value = parseInt(input_num.value) - 1;
    }

};

$(function () {
    window.location.hash = "#moreMerchant";
});


function to_collection(book_id) {
    // console.log(book_id)
    star_status = document.getElementById('star').getAttribute('class');
    // console.log(star_status);
    if ('glyphicon glyphicon-star-emptyglyphicon glyphicon-star-empty' === star_status) {
        $.ajax({
            url: $SCRIPT_ROOT + '/to_collection',
            type: "post",
            data: {book_id: book_id},
            dataType: 'json',
            async: true,
            success: function (data) {
                span_id = document.getElementById('star');
                span_id.setAttribute('class', 'glyphicon glyphicon-star')
            },
            error: function (e) {
                if (e.responseText.indexOf('登录')) {
                    window.location.href = $SCRIPT_ROOT + '/user_login_register/login';
                }
                // alert("收藏失败，请稍后再试～");
            }
        });
    } else {
        $.ajax({
            url: $SCRIPT_ROOT + '/clear_collection',
            type: "post",
            data: {book_id: book_id},
            dataType: 'json',
            async: true,
            success: function (data) {
                span_id = document.getElementById('star');
                span_id.setAttribute('class', 'glyphicon glyphicon-star-emptyglyphicon glyphicon-star-empty')
            },
            error: function (data) {
                if (e.responseText.indexOf('登录')) {
                    window.location.href = $SCRIPT_ROOT + '/user_login_register/login';
                }
            }
        });
    }
}