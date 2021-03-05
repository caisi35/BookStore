// 参考
// https://blog.csdn.net/Shsgear/article/details/53038447
var oScore = document.getElementById("score");
var oTip = document.getElementById("tip");
var oLi = oScore.getElementsByTagName('li');
var oStrong = oScore.getElementsByTagName('strong');
var oSpan = oScore.getElementsByTagName('span')[0];
var oInput = document.getElementById('evaluate_star');
var iScore = iPoint = 0;
var msg = ['1星  非常糟糕', '2星  糟糕', '3星  一般', '4星  商品良好', '5星  非常棒'];
var review = ['1星满意度,请联系我们', '2星满意度,请联系我们', '3星满意度,还不满意？？', '4星满意度,会再接再厉', '5星满意度,会继续努力哒'];
for (var i = 0; i < oLi.length; i++) {
    oLi[i].index = i;
    oLi[i].onmouseover = function () {
        iScore = this.index + 1;             //记录下索引值
        fnPoint(iScore);                   //鼠标移过显示评分
        oTip.style.display = 'block';        //让提示框显示在对应的位置
        oTip.style.left = 160 + this.index * 48 + 'px';
        oStrong[1].innerHTML = msg[this.index];  //移过不同的星星显示对应的文字
        console.log(this.index)
    }
    oLi[i].onclick = function () {
        oStrong[0].innerHTML = review[this.index]; //右上角评价结果显示
        iPoint = this.index + 1;       //鼠标点击事件，记录下索引，并返回索引值
        oInput.value = iPoint;
        return iPoint;

    }
    oLi[i].onmouseout = function () {  //接收点击的索引，鼠标移出后，恢复上次的评分
        fnPoint(iPoint);
        oTip.style.display = 'none';     //鼠标移出隐藏提示框
    }

}

function fnPoint(arg) {
    iScore = arg ? arg : iScore;        //接收一个参数，如果没传进参数就用iScore
    for (var i = 0; i < oLi.length; i++) {   //遍历oLi,对点击的和之前的都亮起来，之后的不亮
        oLi[i].className = i < iScore ? 'current' : '';
    }
}