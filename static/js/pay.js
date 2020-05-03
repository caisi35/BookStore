// 去支付按钮链接
function to_pay() {

    var addr_id = $('#addr_id').text();
    if (addr_id.length === 24) {
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
            window.location.href = $SCRIPT_ROOT + 'order?order_no=' + order_no1;
        } else {
            window.location.href = $SCRIPT_ROOT + 'order?order_no=' + order_no1;
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
        var province = $('span.province').text();
        var city = $('span.city').text();
        var details = $('span.details').text();
        document.getElementById('addr_name').setAttribute('value', name);
        document.getElementById('addr_tel').setAttribute('value', tel);
        document.getElementById('addr_details').setAttribute('value', details);

        objprovince.options[0] = new Option(province, province);
        for (i = 0; i < parray.length; i++) {
            objprovince.options[i + 1] = new Option(parray[i], parray[i]);
        }
        objcity.options[0] = new Option(city);
        $('.add_address').show();
    });
    $('.addr_close,#cancel').click(function () {
        document.getElementById('addr_name').setAttribute('value', '');
        document.getElementById('addr_tel').setAttribute('value', '');
        document.getElementById('addr_details').setAttribute('value', '');
        objprovince.options[0] = new Option("请选择省份");
        objcity.options[0] = new Option("请选择城市");
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

var parray = Array(
    "北京",
    "上海",
    "天津",
    "重庆",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "宁夏",
    "青海",
    "新疆",
    "香港",
    "澳门",
    "台湾"
);

var carray = Array(
    "北京,东城,西城,崇文,宣武,朝阳,丰台,石景山,海淀,门头沟,房山,通州,顺义,昌平,大兴,平谷,怀柔,密云,延庆",
    "上海,黄浦,卢湾,徐汇,长宁,静安,普陀,闸北,虹口,杨浦,闵行,宝山,嘉定,浦东,金山,松江,青浦,南汇,奉贤,崇明",
    "天津,和平,东丽,河东,西青,河西,津南,南开,北辰,河北,武清,红挢,塘沽,汉沽,大港,宁河,静海,宝坻,蓟县,大邱庄",
    "重庆,万州,涪陵,渝中,大渡口,江北,沙坪坝,九龙坡,南岸,北碚,万盛,双挢,渝北,巴南,黔江,长寿,綦江,潼南,铜梁,大足,荣昌,壁山,梁平,城口,丰都,垫江,武隆,忠县,开县,云阳,奉节,巫山,巫溪,石柱,秀山,酉阳,彭水,江津,合川,永川,南川",
    "石家庄,邯郸,邢台,保定,张家口,承德,廊坊,唐山,秦皇岛,沧州,衡水",
    "太原,大同,阳泉,长治,晋城,朔州,吕梁,忻州,晋中,临汾,运城",
    "呼和浩特,包头,乌海,赤峰,呼伦贝尔盟,阿拉善盟,哲里木盟,兴安盟,乌兰察布盟,锡林郭勒盟,巴彦淖尔盟,伊克昭盟",
    "沈阳,大连,鞍山,抚顺,本溪,丹东,锦州,营口,阜新,辽阳,盘锦,铁岭,朝阳,葫芦岛",
    "长春,吉林,四平,辽源,通化,白山,松原,白城,延边",
    "哈尔滨,齐齐哈尔,牡丹江,佳木斯,大庆,绥化,鹤岗,鸡西,黑河,双鸭山,伊春,七台河,大兴安岭",
    "南京,镇江,苏州,南通,扬州,盐城,徐州,连云港,常州,无锡,宿迁,泰州,淮安",
    "杭州,宁波,温州,嘉兴,湖州,绍兴,金华,衢州,舟山,台州,丽水",
    "合肥,芜湖,蚌埠,马鞍山,淮北,铜陵,安庆,黄山,滁州,宿州,池州,淮南,巢湖,阜阳,六安,宣城,亳州",
    "福州,厦门,莆田,三明,泉州,漳州,南平,龙岩,宁德",
    "南昌市,景德镇,九江,鹰潭,萍乡,新馀,赣州,吉安,宜春,抚州,上饶",
    "济南,青岛,淄博,枣庄,东营,烟台,潍坊,济宁,泰安,威海,日照,莱芜,临沂,德州,聊城,滨州,菏泽,博兴",
    "郑州,开封,洛阳,平顶山,安阳,鹤壁,新乡,焦作,濮阳,许昌,漯河,三门峡,南阳,商丘,信阳,周口,驻马店,济源",
    "武汉,宜昌,荆州,襄樊,黄石,荆门,黄冈,十堰,恩施,潜江,天门,仙桃,随州,咸宁,孝感,鄂州",
    "长沙,常德,株洲,湘潭,衡阳,岳阳,邵阳,益阳,娄底,怀化,郴州,永州,湘西,张家界",
    "广州,深圳,珠海,汕头,东莞,中山,佛山,韶关,江门,湛江,茂名,肇庆,惠州,梅州,汕尾,河源,阳江,清远,潮州,揭阳,云浮",
    "南宁,柳州,桂林,梧州,北海,防城港,钦州,贵港,玉林,南宁地区,柳州地区,贺州,百色,河池,来宾",
    "海口,三亚",
    "成都,绵阳,德阳,自贡,攀枝花,广元,内江,乐山,南充,宜宾,广安,达川,雅安,眉山,甘孜,凉山,泸州",
    "贵阳,六盘水,遵义,安顺,铜仁,黔西南,毕节,黔东南,黔南",
    "昆明,大理,曲靖,玉溪,昭通,楚雄,红河,文山,思茅,西双版纳,保山,德宏,丽江,怒江,迪庆,临沧",
    "拉萨,日喀则,山南,林芝,昌都,阿里,那曲",
    "西安,宝鸡,咸阳,铜川,渭南,延安,榆林,汉中,安康,商洛",
    "兰州,嘉峪关,金昌,白银,天水,酒泉,张掖,武威,定西,陇南,平凉,庆阳,临夏,甘南",
    "银川,石嘴山,吴忠,固原",
    "西宁,海东,海南,海北,黄南,玉树,果洛,海西",
    "乌鲁木齐,石河子,克拉玛依,伊犁,巴音郭勒,昌吉,克孜勒苏柯尔克孜,博 尔塔拉,吐鲁番,哈密,喀什,和田,阿克苏",
    "香港",
    "澳门",
    "台北,高雄,台中,台南,屏东,南投,云林,新竹,彰化,苗栗,嘉义,花莲,桃园,宜兰,基隆,台东,金门,马祖,澎湖"
);
objprovince.onchange = function GetCity() {
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


function GetProvince() {
    objprovince.options[0] = new Option("请选择省份", "请选择省份");
    for (i = 0; i < parray.length; i++) {
        objprovince.options[i + 1] = new Option(parray[i], parray[i]);
    }
}

window.onload = GetProvince();