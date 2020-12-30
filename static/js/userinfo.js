// ****************用户信息编辑*****************************
$(function () {
    $('#change_pw_btn').click(function () {
        $('.change-pw').show();
    });
    $('a.close,button.close').click(function () {
        $('.change-pw').hide()
    })
});

$(function () {
    $('#edit-info').click(function () {
        $('.change-info').show();
    });
    $('a.close,button.close').click(function () {
        $('.change-info').hide()
    })
});

// ****************收货人信息*****************************
function addressDelete(_id) {
    if (confirm('确认要删除？')) {
        $.ajax({
            url: $SCRIPT_ROOT + '/userInfo/addressDelete',
            type: 'post',
            dataType: 'json',
            sync: false,
            data: {'_id': _id},
            success: function (result) {
                if (result) {
                    // 成功重新加载页面
                    window.location.reload()
                } else {
                    alert('删除错误，请重试！')
                }
            },
            error: function (e) {
                alert('操作错误：' + e)
            }
        })
    }
}

function addressDefault(_id) {
    $.ajax({
        url: $SCRIPT_ROOT + '/userInfo/addressDefault',
        type: 'post',
        dataType: 'json',
        data: {'_id': _id},
        sync: false,
        success: function (result) {
            if (result) {
                // 成功重新加载页面
                window.location.reload()
            } else {
                alert('删除错误，请重试！')
            }
        },
        error: function (e) {
            alert('操作错误：' + e)
        }
    })
}

// ****************改变province选择*****************************


function changeProvince(s) {
    var option_default = document.getElementById('option-default');
    option_default.remove();
    for (i = 0; i < parray.length; i++) {
        s.options[i + 1] = new Option(parray[i], parray[i]);
    }
    s.onchange = function GetCity() {
        var x = this.selectedIndex - 1;
        for (i = 0; i < objcity.length; i++) {
            objcity.remove(i);
        }
        if (x >= 0) {
            var citylist = carray[x].split(',');

            for (i = 0; i < citylist.length; i++) {
                objcity.options[i] = new Option(citylist[i], citylist[i]);
            }
        } else {
            objcity.options[0] = new Option("请选择城市", "请选择城市");
        }
    };
}

// ********************************添加收货地址********************************
$(function () {
    $('#new_addr').click(function () {
        $('.add_address').show();
    });
    $('.close,#cancel').click(function () {
        $('.add_address').hide();
    })
});

// ********************************确认删除订单********************************
function deleteOrder(order_no) {
    if (confirm('您确认要删除此订单？')) {
        $.ajax({
            url: $SCRIPT_ROOT + 'deleteOrder',
            type: 'post',
            dataType: 'json',
            data: {'order_no': order_no},
            sync: false,
            success: function (result) {
                if (result) {
                    window.location.reload()
                } else {
                    alert('操作失败！')
                }
            },
            error: function (e) {
                alert('操作错误，请重试！')
            }
        })
    } else {

    }
}

function deleteOrders() {
    var orders_no = new Array();
    var inputs = document.getElementsByName("checkbox1");
    var is_checked = false;
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked === true) {
            orders_no.push($(inputs[i]).next().val());
            is_checked = true;
        }
    }
    if (is_checked) {
        if (confirm('确定要删除？')){
            $.ajax({
                url: $SCRIPT_ROOT + 'deleteOrders',
                type: 'post',
                dataType: 'json',
                data: {'orders_no': orders_no},
                sync: false,
                success: function (result) {
                    if (result) {
                        window.location.reload()
                    } else {
                        alert('操作失误！')
                    }
                },
                error: function (e) {
                    alert('操作错误，请重试！')
                }
            })
        }
    } else {
        alert('您还没有选中订单呢！')
    }
}

//******************** 订单*******************
Date.prototype.Format = function (fmt) { //author: meizz
            var o = {
                "M+": this.getMonth() + 1, //月份
                "d+": this.getDate(), //日
                "h+": this.getHours(), //小时
                "m+": this.getMinutes(), //分
                "s+": this.getSeconds(), //秒
                "q+": Math.floor((this.getMonth() + 3) / 3), //季度
                "S": this.getMilliseconds() //毫秒
            };
            if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
            for (var k in o)
                if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
            return fmt;
        }

        function countDown(maxtime, fn, endtime) {
            var timer = setInterval(function () {
                if (!!maxtime && maxtime >= 0) {
                    var day = Math.floor(maxtime / 86400),
                        hour = Math.floor((maxtime % 86400) / 3600),
                        minutes = Math.floor((maxtime % 3600) / 60),
                        seconds = Math.floor(maxtime % 60),
                        msg = day + "天" + hour + "时" + minutes + "分" + seconds + "秒"+'<br>';
                    fn(msg);
                    --maxtime;
                } else {
                    clearInterval(timer);
                    fn(false);
                }
            }, 1000);
        }
