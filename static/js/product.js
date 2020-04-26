// // product 加减按钮
var num_jia = document.getElementById("add");
var num_jian = document.getElementById("cut");
var input_num = document.getElementById("num");
num_jia.onclick = function () {
    input_num.value = parseInt(input_num.value) + 1;
};
num_jian.onclick = function () {

    if (input_num.value <= 1) {
        input_num.value = 1;
    } else {
        input_num.value = parseInt(input_num.value) - 1;
    }

};

