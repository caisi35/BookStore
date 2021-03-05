// 倒计时
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
};

// 时间格式化
function countDown(maxtime, fn, endtime) {
    var timer = setInterval(function () {
        if (!!maxtime && maxtime >= 0) {
            var day = Math.floor(maxtime / 86400),
                hour = Math.floor((maxtime % 86400) / 3600),
                minutes = Math.floor((maxtime % 3600) / 60),
                seconds = Math.floor(maxtime % 60),
                msg = hour + "时" + minutes + "分" + seconds + "秒" + '<br>';
            fn(msg);
            --maxtime;
        } else {
            clearInterval(timer);
            fn(false);
        }
    }, 1000);
}

// orderDetails 显示图书内容(li_id,span_id)
function showmouseevent(btn, box) {
    var timer = null;
    box.onmouseover = btn.onmouseover = function () {
        if (timer) clearTimeout(timer);
        box.style.display = 'block';
        box.style.position = 'relative';
        btn.style.border = '1px solid';
        btn.style.backgroundColor = 'white';
        box.style.width = '200px'
    };
    box.onmouseout = btn.onmouseout = function () {
        timer = setTimeout(function () {
            box.style.display = 'none';
            btn.style.border = '0px solid';

        }, 400);
    }
}
