// 去支付按钮链接
function to_pay() {

    var amount = document.getElementById("amount_pay");
    $.ajax({
        url: $SCRIPT_ROOT + '/to_pay',
        type: "post",
        data: {amount_pay: amount.innerText, books: books_},
        dataType: 'json',
        async: false,
        success: function (data) {
            var order_no = data.result;
            window.location.href = $SCRIPT_ROOT + '/pay?order_no=' + order_no;
        },
        error: function (e) {
            alert("error:" + e);
        }
    });
}

// 支付弹窗
$(function () {
    $('button').click(function () {
        $('.pay_QR').show();
    });
    $('.close,#cancel').click(function () {
        $('.pay_QR').hide();
    })
});

function pay_click() {
    var check_pay = document.getElementsByClassName('pay_input');
    for (var i = 0; i < check_pay.length; i++) {
        if (check_pay[i].checked === true) {
            check_pay[i].parentElement.style.border = '2px solid red';
        } else {
            check_pay[i].parentElement.style.border = '0px solid red';
        }
    }
}

function pay_method_fun() {
    var check_pay = document.getElementsByClassName('pay_input');
    for (var i = 0; i < check_pay.length; i++) {
        if (check_pay[i].checked == true && check_pay[i].value === '微信支付') {
            $('#pay_img_QR').src='/static/images/pay/weixin_payQR.png';
            $('#pay_title_fun').text('微信扫码支付')
        } else if (check_pay[i].checked == true && check_pay[i].value === '支付宝支付') {
            $('#pay_img_QR').src='/static/images/pay/zhifubao_payQR.png';
            $('#pay_title_fun').text('支付宝扫码支付')
        }
    }
}

function to_orders(order_no1) {
    var check_pay_order = document.getElementsByClassName('pay_input');
    for (var i = 0; i < check_pay_order.length; i++) {
        if (check_pay_order[i].checked == true) {
            window.location.href = $SCRIPT_ROOT+'order?order_no='+order_no1;
        }else {
            window.location.href = $SCRIPT_ROOT+'order?order_no='+order_no1;
        }
    }
}