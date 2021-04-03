
// 设置导航栏吸顶及返回顶部功能
window.onload = function () {
    var top_id = document.getElementById("to_top_btn");
    top_id.style.display = "none";

    ///*导航栏吸顶*/
    var nav = document.getElementById("nav");
    var navTop = nav.offsetTop;

    var timer = null;
    top_id.onclick = function () {
        timer = setInterval(function () {
            var backTop = document.documentElement.scrollTop || document.body.scrollTop;
            var speedTop = backTop / 5;
            document.documentElement.scrollTop = backTop - speedTop;
            if (backTop == 0) {
                clearInterval(timer);
            }
        }, 30);
    };
    var pageHeight = 500;
    window.onscroll = function () {
        var backTop = document.documentElement.scrollTop || document.body.scrollTop;
        if (backTop > pageHeight) {
            top_id.style.display = "block";
        } else {
            top_id.style.display = "none";
        }
        //吸顶效果
        if (backTop >= navTop) {
            nav.style.position = "fixed";
            nav.style.top = "0";
            nav.style.left = "0";
            nav.style.zIndex = "100";
        } else {
            nav.style.position = "";
        }
    };

    // 选项卡
    function $(id){
    return typeof id === 'string' ? document.getElementById(id):id;
}
        // 拿到所有的标题(li标签) 和 标题对应的内容(div)
    var titles = $('tab-header').getElementsByTagName('li');
    var divs = $('tab-content').getElementsByClassName('dom');
    // 判断
    if(titles.length != divs.length)
        return;
    // 遍历
    for(var i=0; i<titles.length; i++){
        // 取出li标签
        var li = titles[i];
        li.id = i;
        // console.log(li);
        // 监听鼠标的移动
        li.onmousemove = function(){
            for(var j=0; j<titles.length; j++){
                titles[j].className = '';
                divs[j].style.display = 'none';
            }
            this.className = 'selected';
            divs[this.id].style.display = 'block';
        }
    }
};
