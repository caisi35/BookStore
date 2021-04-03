// 复选框选择按钮函数
function allSelect(check_v, checkname) {
    var v_item = document.getElementsByName(check_v);
    var items = document.getElementsByName(checkname);
    for (var i = 0; i < items.length; ++i) {
        if (v_item[0].checked) {
            items[i].checked = true;
        } else {
            items[i].checked = false;
        }
    }
}

function singleSelect2parent(check_v, checkname) {
    var v_item = document.getElementsByName(check_v);
    var items = document.getElementsByName(checkname);
    var childStatus = true;
    for (var i = 0; i < items.length; ++i) {
        childStatus = (childStatus && items[i].checked);
    }
    if (childStatus) {
        v_item[0].checked = true;
    } else {
        v_item[0].checked = false;
    }
}

//购物车数量、总价计算
//1、定义全选的插件
jQuery.fn.extend({
    bindCheck: function ($subCheckBox, $btnUncheck) {
        let $allCheckBox = this;
        //1、给全选复选框绑定click事件
        //this:是全选复选框（jQuery对象）
        this.click(function () {
            let isChecked = this.checked;
            $subCheckBox.each(function () {
                this.checked = isChecked;
            });
        });
        //2、给反选
        if (arguments.length == 2) {
            $btnUncheck.click(function () {
                $subCheckBox.each(function () {
                    this.checked = !this.checked;
                });
                reversCheck();
            });
        }
        //3、给每个选择项的复选框绑定事件
        $subCheckBox.click(function () {
            reversCheck();
        });

        function reversCheck() {
            //1、判断是否全部的复选框被选中
            let isAllChecked = true;
            $subCheckBox.each(function () {
                if (!this.checked) {
                    isAllChecked = false;
                }
            });
            //2、处理全选复选框
            $allCheckBox.attr("checked", isAllChecked);
        }
    }
});
$(function () {
    $(".delete-collection").click(function () {//点击删除的按钮
        var inputs = document.getElementsByName("checkbox1");
        var is_checked = false;
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].checked === true) {
                book_ids.push($(inputs[i]).next().val());
                is_checked = true;
            }
        }
        if (is_checked) {
            $(this).click(function () {
                if (confirm("您确定要移除收藏？")) {
                    // 获取所有book id
                    var book_ids = new Array();
                    // console.log(book_ids);
                    count = delete_collection(book_id = book_ids);
                    if (count) {
                        window.location.reload();
                    }
                }
            });
        }else{
            alert('您还没有选中物品呢,请选择您的物品~')
        }
    });

    function delete_collection(book_id) {
        $.ajax({
            url: $SCRIPT_ROOT + '/userInfo/delete_collection',
            type: "post",
            data: {collection_ids: book_id},
            dataType: 'json',
            async: false,
            success: function (data) {
                console.log(data);
                if (data) {
                    window.location.reload();
                } else {
                    alert('出错了，请稍后再试～')
                }
            },
            error: function (e) {
                alert("error");
            }
        });
        // this_obj.html(r);
        return r;
    }
});

// 购物车选择下单物品，转结算页面
function to_buy() {
    var book_ids = new Array();
    var inputs = document.getElementsByName("checkbox1");
    var is_checked = false;
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked === true) {
            book_ids.push($(inputs[i]).next().val());
            is_checked = true;
        }
    }
    if (is_checked) {
        window.location.href = $SCRIPT_ROOT + '/buy_list?book_id=' + book_ids;
    } else {
        alert('您还没有选中物品呢,请选择您的物品！')
    }
}

