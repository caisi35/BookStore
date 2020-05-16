

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
                console.log('DeleteUser Error:'+e)
            }
        })
    }
}