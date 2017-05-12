

$('.jian-huifu').on('click', function(event) {
    var mesg = $('.textarea').text().trim();
    if (mesg=='') {
        $.alert("发送信息不能为空");
        return;
    };

    var name = $('#name').html().trim();
    var time = getNowFormatDate();
    var img_src = $('.jian-item-me-img').attr('src');
    //1.ajax操作发送信息

    //2.更新聊天界面

    var mesg_dom = '<div class="jian-chat-item"><table width="100%"><tr><td rowspan="2" valign="top" width="40px;"><img src="'+img_src+'" class="jian-chat-img"></td><td><div class="jian-chat-name">'+name+'</div></td><td><div class="jian-chat-time">'+time+'</div></td></tr><tr><td colspan="2"><div class="jian-chat-content">'+mesg+'</div></td></tr></table></div>';
    $('.jian-chat-liuyan').after(mesg_dom);

    $('.textarea').html('')
});


//获取当前系统时间：如：2016-08-07 01:56
function getNowFormatDate() {
    var date = new Date();
    var seperator1 = "-";
    var seperator2 = ":";
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    var hours = date.getHours();
    var mins = date.getMinutes();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    if (hours >= 1 && hours <= 9) {
        hours = "0" + hours;
    }
    if (mins >= 1 && mins <= 9) {
        mins = "0" + mins;
    }
    var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
            + " " + hours + seperator2 + mins;
    return currentdate;
}

