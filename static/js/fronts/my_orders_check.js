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