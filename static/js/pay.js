// 去支付按钮链接
function to_pay(is_buy_now) {

    var addr_id = $('#addr_id').text();
    console.log(is_buy_now);
    if (addr_id.length === 24) {
        $.ajax({
            url: $SCRIPT_ROOT + '/to_pay',
            type: "POST",
            data: {books: books_, addr_id: addr_id, is_buy_now: is_buy_now},
            dataType: 'json',
            success: function (data) {
                var order_no = data.result;
                window.location.href = $SCRIPT_ROOT + '/pay?order_no=' + order_no;
            },
            error: function (e) {
                alert("error:" + e);
            }
        });
    }else{
        alert('请添加收货人信息！ ');
        $('#go-to-pay-btn').setAttribute('disabled', true);

    }
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
        if (check_pay[i].checked === true && check_pay[i].value === '微信支付') {
            $('img#pay_img_QR').attr('src', '/static/images/pay/weixin_payQR.png');
            $('#pay_title_fun').text('微信扫码支付')
        } else if (check_pay[i].checked === true && check_pay[i].value === '支付宝支付') {
            $('img#pay_img_QR').attr('src', '/static/images/pay/zhifubao_payQR.png');
            $('#pay_title_fun').text('支付宝扫码支付')
        }
    }
}

function to_orders(order_no1) {
    var check_pay_order = document.getElementsByClassName('pay_input');
    for (var i = 0; i < check_pay_order.length; i++) {
        if (check_pay_order[i].checked === true) {
            window.location.href = $SCRIPT_ROOT + '/orders/orderDetails?order_no=' + order_no1;
        } else {
            window.location.href = $SCRIPT_ROOT + '/orders/orderDetails?order_no=' + order_no1;
        }
    }
}

// 添加收货地址
$(function () {
    $('#new_addr').click(function () {
        $('.add_address').show();
    });
    $('.addr_close,#cancel').click(function () {
        $('.add_address').hide();
    })
});
// 编辑收货地址
$(function () {
    $('.addr_edit').click(function () {
        var name = $('span.name').text();
        var tel = $('span.tel').text();
        var district = $('span.district').text();
        var province = $('span.province').text();
        var city = $('span.city').text();
        var details = $('span.details').text();
        document.getElementById('addr_name').setAttribute('value', name);
        document.getElementById('addr_tel').setAttribute('value', tel);
        document.getElementById('addr_details').setAttribute('value', details);
        document.getElementById('J_Address2').setAttribute('value', province+" "+city+" "+district);

        // objprovince.options[0] = new Option(province, province);
        // for (i = 0; i < parray.length; i++) {
        //     objprovince.options[i + 1] = new Option(parray[i], parray[i]);
        // }
        // objcity.options[0] = new Option(city);
        $('.add_address').show();
    });
    $('.addr_close,#cancel').click(function () {
        document.getElementById('addr_name').setAttribute('value', '');
        document.getElementById('addr_tel').setAttribute('value', '');
        document.getElementById('addr_details').setAttribute('value', '');
        document.getElementById('J_Address2').setAttribute('value', '');
        // objprovince.options[0] = new Option("请选择省份");
        // objcity.options[0] = new Option("请选择城市");
        $('.add_address').hide();
    })
});

// 删除默认收货地址
$('.addr_delete').click(function () {
    if (confirm("您确定要删除？")) {
        var _id = $('#addr_id').text();
        $.ajax({
            url: $SCRIPT_ROOT + '/addr_delete',
            type: 'post',
            data: {'_id': _id},
            dataType: 'json',
            async: false,
            success: function (data) {
                window.location.reload()
            },
            error: function (data) {
                alert('删除失败，请重试！')
            }
        })
    }
});


// 订单所在地址
var objprovince = document.getElementById("province");
var objcity = document.getElementById("city");

