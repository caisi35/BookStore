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
    $("#table tbody tr td .adds").each(function () { //点击增加的按钮
        $(this).click(function () {
            //1.改变数量
            var count = parseFloat($(this).parents("tr").find(".span").html());
            var book_id = $(this).parents("span").find("input[name='book_id']").val();
            count = adds(count, 'adds', book_id = book_id);
            $(this).parent("span").find(".span").html(count);
            //2.改小计
            var price = parseFloat($(this).parents("tr").find(".price").html());
            var money = (price * count).toFixed(2);
            $(this).parents("tr").find(".prices").html(money);
            //3.改总价
            total();
            countAll();//最后的总数量
        });
    });
    $(".reduces").each(function () {//点击减少的按钮
        $(this).click(function () {
            //1.改变数量
            var count = parseFloat($(this).parents("tr").find(".span").html());
            var m = 'reduces';
            var book_id = $(this).parents("span").find("input[name='book_id']").val();
            if (count == 1 && confirm("您确定要移除该物品？")) {
                count = adds(count, 'delete', book_id = book_id);
                $(this).parents("tr").remove();
            } else if (count > 1) {
                count = adds(count, 'reduces', book_id = book_id);
            }
            $(this).parent("span").find(".span").html(count);
            //2.改小计
            var price = parseFloat($(this).parents("tr").find(".price").html());
            var money = (price * count).toFixed(2);
            $(this).parents("tr").find(".prices").html(money);
            total();
            countAll();//最后的总数量
        });
    });
    // {#当刷新页面后统计选中着的total countAll#}
    window.onload = function () {
        //合计
        total();
        countAll();
    };

    //num ajax function to update database
    /**
     * 同步修改购物车与数据库中的图书数量，每次修改的数量为1
     * count 参数传入当前的数量
     * method 操作方法 可选加、减、删除（‘adds’，‘reduces’，‘delete’）
     * book_id 需要修改的图书id
     *
     * */
    function adds(count, method, book_id) {
        $.ajax({
            url: $SCRIPT_ROOT + '/count_numbers',
            type: "post",
            data: {count_: count, method_: method, book_id: book_id},
            dataType: 'json',
            async: false,
            success: function (data) {
                r = parseInt(data.result);
            },
            error: function (e) {
                alert("error");
                r = count
            }
        });
        // this_obj.html(r);
        return r;
    }

    //合计
    function total() {
        let sum = 0;
        $(".prices").each(function () {//先循环每个小计
            if (($(this).parents("tr").find(".dan_select")).prop("checked")) {//判断复选框有没有选中
                sum += parseFloat($(this).html());
            }
            $(".sum_mon").html(sum.toFixed(2));
        });
    }


    //总数量
    function countAll() {
        let counts = 0;
        for (let i = 0; i < $(".dan_select").length; i++) {
            if ($(".dan_select")[i].checked == true) { //注意此块用jquery不好实现
                counts += parseInt($('.span')[i].innerHTML);
            }
        }
        $("#count")[0].innerHTML = counts;
    }

    //全选插件(引入插件Allcheck.js)
    $(".checkOnly").bindCheck($("#table :checkbox"));
    //当点击复选框时调用total()
    $(".check").each(function () {
        $(this).click(function () {
            let num = 0;
            $(".check").each(function () {
                if ($(this).prop("checked")) {
                    num++;
                }
                countAll();
                total();
                compare(); //最贵的
            });
            if (num == $(".check").length) {//如果复选框的长度与num相等时，全选那个按钮也会被选中
                $(".checkOnly")[0].checked = true;
                compare(); //最贵的
                countAll(); //总数量
                total();
            } else {
                $(".checkOnly")[0].checked = false;
            }
        });
    });
    $(".checkOnly").click(function () {
        total();
        countAll(); //总数量
    });
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
    }else {
        alert('您还没有选中物品呢,请选择您的物品！')
    }
}

