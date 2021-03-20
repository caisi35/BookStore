function submit_auth(role, email) {
    var status = document.getElementById(email + role);
    // console.log(status.value);
    $.ajax({
        url: $SCRIPT_ROOT + '/admin/userAdmin/admin_account',
        type: "post",
        data: {email: email, role: role, status: status.value},
        dataType: 'json',
        async: true,
        success: function (data) {
            // console.log(data);
            if (data === false) {
                alert('出错了！请重试');
                window.location.reload();
            }

            if (data.status !== 'on') {
                status.value = 'off';
                status.removeAttribute('checked')
            } else {
                status.value = 'on';
                status.setAttribute('checked', '')
            }
        },
        error: function (e) {
            alert("error!");
            if (status.value === 'on') {
                status.setAttribute('checked', '')
            } else {
                status.value = 'off';
                status.removeAttribute('checked')
            }
        }
    });
}