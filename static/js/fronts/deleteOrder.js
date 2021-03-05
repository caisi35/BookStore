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
                    window.location.href = $SCRIPT_ROOT + '/orders'
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