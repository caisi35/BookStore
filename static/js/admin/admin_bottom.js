// 删除用户
function deleteUser(id) {
    if(confirm('您确定要删除该用户？')){
        $.ajax({
            url: $SCRIPT_ROOT+'/admin/userAdmin/delete_user',
            type:'post',
            dataType:'json',
            data:{'id': id},
            success:function (result) {
                if (result){
                    alert('删除成功');
                    window.location.reload()
                }else{
                    alert('操作失败');
                }
            },
            error:function (e) {
                console.log('DeleteUser Error:'+e.toString())
            }
        })
    }
}

// 重置用户密码
function resetPwd(id) {
    if(confirm('您确定要重置该用户的密码？')){
        $.ajax({
            url: $SCRIPT_ROOT+'/admin/userAdmin/reset_pwd',
            type:'post',
            dataType:'json',
            data:{'id': id},
            success:function (result) {
                if (result['result']){
                    alert('重置成功，新密码为：'+result['password']);
                }else{
                    alert('操作失败'+result);
                }
            },
            error:function (e) {
                console.log('DeleteUser Error:'+e.toString())
            }
        })
    }
}
// 冻结账户
function freezing_user(id) {
        if(confirm('您确定要冻结该账户吗？')){
        $.ajax({
            url: $SCRIPT_ROOT+'/admin/userAdmin/freezing',
            type:'post',
            dataType:'json',
            data:{'id': id},
            success:function (result) {
                if (result){
                    alert('冻结成功！');
                    window.location.reload();
                }else{
                    alert('操作失败'+result);
                }
            },
            error:function (e) {
                console.log('DeleteUser Error:'+e.toString())
            }
        })
    }
}

// 激活账户
function activate_user(id) {
        if(confirm('您确定要激活该账户吗？')){
        $.ajax({
            url: $SCRIPT_ROOT+'/admin/userAdmin/activate_user',
            type:'post',
            dataType:'json',
            data:{'id': id},
            success:function (result) {
                if (result){
                    alert('激活成功！');
                    window.location.reload();
                }else{
                    alert('操作失败'+result);
                }
            },
            error:function (e) {
                console.log('DeleteUser Error:'+e.toString())
            }
        })
    }
}

// 显示选择上传后的图片
function changepic(obj) {
    //console.log(obj.files[0]);//这里可以获取上传文件的name
    var newsrc=getObjectURL(obj.files[0]);
    var img = document.getElementById('show').src=newsrc;
    $('.upload-div').show();
}
//建立一個可存取到該file的url
function getObjectURL(file) {
    var url = null ;
    // 下面函数执行的效果是一样的，只是需要针对不同的浏览器执行不同的 js 函数而已
    if (window.createObjectURL!=undefined) { // basic
        url = window.createObjectURL(file) ;
    } else if (window.URL!=undefined) { // mozilla(firefox)
        url = window.URL.createObjectURL(file) ;
    } else if (window.webkitURL!=undefined) { // webkit or chrome
        url = window.webkitURL.createObjectURL(file) ;
    }
    return url ;
}