// 删除用户
function deleteUser(id) {
    if(confirm('您确定要删除该用户？')){
        $.ajax({
            url: $SCRIPT_ROOT+'/admin/delete_user',
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
            url: $SCRIPT_ROOT+'/admin/reset_pwd',
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
            url: $SCRIPT_ROOT+'/admin/freezing',
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
            url: $SCRIPT_ROOT+'/admin/activate_user',
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

