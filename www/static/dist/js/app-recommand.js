//第一个
var timer1;
var second1 = '0';

function reset_luyin1() {
    $('#play_luyin1').attr('src', 'http://res.jian-hu.cn/static/img/luyin@2x.png');
    $('#yilu_label1').html("点击即录音，最多60秒");
    second1 = '0';
    $('#play_luyin1').attr('id', 'start_luyin1');
    $('#chonglu1').html('');
}


function start_luyin1_callback(event, _this) {
    _this.attr('id', "play_luyin1");
    //1.更新点击录音图片，实现360度旋转
    _this.attr('src', 'http://res.jian-hu.cn/static/img/luyinzhong@3x.gif');
    //2.更新点击开始录音文本
    timedCount1();
    $('#yilu_label1').html('已录 <font style="color: #ff9600;" id="count1">0</font> 秒');
    //3.更新将左边空白部分替换成暂停图片按钮
    var start = '<div class="jian-luyin-start-img" id="jian-luyin-stop1"><img src="http://res.jian-hu.cn/static/img/stop@2x.png" class="jian-luyin-stop"></div>';
    $('#luyin-stop1').html(start);
    //右边的重录按钮消失
    $('#chonglu1').html('');
}


function luyin_stop1_callback(event, _this) {
    clearTimeout(timer1);
    second1 = isNaN(second1) ? '0' : second1;
    $('#play_luyin1').attr('src', 'http://res.jian-hu.cn/static/img/bofang@2x.png');
    $('#luyin-stop1').html('');
    $('#chonglu1').html('<div class="jian-luyin-1" id="luyin-chonglu">重录</div>');
    $('#yilu_label1').html('点击播放，已录 <font style="color: #ff9600;" id="count1">' + second1 + '</font> 秒');
}


function luyin_paly1_callback(event, _this) {
    //1.更新点击录音图片，实现360度旋转
    _this.attr('src', 'http://res.jian-hu.cn/static/img/luyinzhong@3x.gif');
    //2.更新点击开始录音文本

    $('#yilu_label1').html('剩余 <font style="color: #ff9600;" id="count1">' + second1 + '</font> 秒');
    setTimeout("timedReverse1()", 1000);
    //3.更新将左边空白部分替换成暂停图片按钮
    var start = '<div class="jian-luyin-start-img" id="jian-play-stop1"><img src="http://res.jian-hu.cn/static/img/stop@2x.png" class="jian-luyin-stop"></div>';
    $('#luyin-stop1').html(start);
    //右边的重录按钮消失
    $('.chonglu1').html('');
}


function Play1Callback(_this) {
    //1.更新点击录音图片，实现360度旋转
    _this.attr('src', 'http://res.jian-hu.cn/static/img/luyinzhong@3x.gif');
    //2.更新点击开始录音文本
    timedReverse1();
    _this.parent().parent().parent().prev().html('剩余 <font style="color: #ff9600;" id="count1">0</font> 秒');
    //3.更新将左边空白部分替换成暂停图片按钮
    var start = '<div class="jian-luyin-start-img" id="jian-luyin-stop"><img src="http://res.jian-hu.cn/static/img/stop@2x.png" class="jian-luyin-stop"></div>';
    _this.parent().parent().prev().html(start);
    //右边的重录按钮消失
    $('.chonglu1').html('');

}


function timedCount1() {
    console.log($('#count1').text() + "ffffffffffffffffffffff");
    second1 = parseInt($('#count1').text()) + 1;
    $('#count1').text(second1);
    if (second1 == 60) {
        clearTimeout(timer1);
        $('#play_luyin1').attr('src', 'http://res.jian-hu.cn/static/img/bofang@2x.png');
        $('#luyin-stop1').html('');
        $('#chonglu1').html('<div class="jian-luyin-1" id="luyin-chonglu">重录</div>');
        $('#yilu_label1').html('点击播放，已录 <font style="color: #ff9600;" id="count1">' + second1 + '</font> 秒');
    } else
        timer1 = setTimeout("timedCount1()", 1000);
}

function timedReverse1() {

    var second = parseInt($('#count1').text()) - 1;
    second = second == -1 ? 0 : second;
    $('#count1').text(second);
    if (second == 0) {
        clearTimeout(timer1);
        $('#play_luyin1').attr('src', 'http://res.jian-hu.cn/static/img/bofang@2x.png');
        $('#luyin-stop1').html('');
        $('#chonglu1').html('<div class="jian-luyin-1" id="luyin-chonglu">重录</div>');
        $('#yilu_label1').html('点击播放，已录 <font style="color: #ff9600;" id="count1">' + second1 + '</font> 秒');
    } else
        timer1 = setTimeout("timedReverse1()", 1000);

}


//第二个


var timer2;
var second2 = '0';

function reset_luyin2() {
    $('#play_luyin2').attr('src', 'http://res.jian-hu.cn/static/img/luyin@2x.png');
    $('#yilu_label2').html("点击即录音，最多60秒");
    second2 = '0';
    $('#play_luyin2').attr('id', 'start_luyin2');
    $('#chonglu2').html('');
}


function start_luyin2_callback(event, _this) {
    _this.attr('id', "play_luyin2");
    //1.更新点击录音图片，实现360度旋转
    _this.attr('src', 'http://res.jian-hu.cn/static/img/luyinzhong@3x.gif');
    //2.更新点击开始录音文本
    timedCount2();
    $('#yilu_label2').html('已录 <font style="color: #ff9600;" id="count2">0</font> 秒');
    //3.更新将左边空白部分替换成暂停图片按钮
    var start = '<div class="jian-luyin-start-img" id="jian-luyin-stop2"><img src="http://res.jian-hu.cn/static/img/stop@2x.png" class="jian-luyin-stop"></div>';
    $('#luyin-stop2').html(start);
    //右边的重录按钮消失
    $('#chonglu2').html('');
}


function luyin_stop2_callback(event, _this) {
    clearTimeout(timer2);
    second2 = isNaN(second2) ? '0' : second2;
    $('#play_luyin2').attr('src', 'http://res.jian-hu.cn/static/img/bofang@2x.png');
    $('#luyin-stop2').html('');
    $('#chonglu2').html('<div class="jian-luyin-2" id="luyin-chonglu">重录</div>');
    $('#yilu_label2').html('点击播放，已录 <font style="color: #ff9600;" id="count2">' + second2 + '</font> 秒');
}


function luyin_paly2_callback(event, _this) {
    //1.更新点击录音图片，实现360度旋转
    _this.attr('src', 'http://res.jian-hu.cn/static/img/luyinzhong@3x.gif');
    //2.更新点击开始录音文本

    $('#yilu_label2').html('剩余 <font style="color: #ff9600;" id="count2">' + second2 + '</font> 秒');
    setTimeout("timedReverse2()", 1000);
    //3.更新将左边空白部分替换成暂停图片按钮
    var start = '<div class="jian-luyin-start-img" id="jian-play-stop2"><img src="http://res.jian-hu.cn/static/img/stop@2x.png" class="jian-luyin-stop"></div>';
    $('#luyin-stop2').html(start);
    //右边的重录按钮消失
    $('.chonglu2').html('');
}


function Play2Callback(_this) {
    //2.更新点击录音图片，实现360度旋转
    _this.attr('src', 'http://res.jian-hu.cn/static/img/luyinzhong@3x.gif');
    //2.更新点击开始录音文本
    timedReverse2();
    _this.parent().parent().parent().prev().html('剩余 <font style="color: #ff9600;" id="count2">0</font> 秒');
    //3.更新将左边空白部分替换成暂停图片按钮
    var start = '<div class="jian-luyin-start-img" id="jian-luyin-stop"><img src="http://res.jian-hu.cn/static/img/stop@2x.png" class="jian-luyin-stop"></div>';
    _this.parent().parent().prev().html(start);
    //右边的重录按钮消失
    $('.chonglu2').html('');

}


function timedCount2() {
    second2 = parseInt($('#count2').text()) + 1;
    $('#count2').text(second2);
    if (second2 == 60) {
        clearTimeout(timer2);
        $('#play_luyin2').attr('src', 'http://res.jian-hu.cn/static/img/bofang@2x.png');
        $('#luyin-stop2').html('');
        $('#chonglu2').html('<div class="jian-luyin-2" id="luyin-chonglu">重录</div>');
        $('#yilu_label2').html('点击播放，已录 <font style="color: #ff9600;" id="count2">' + second2 + '</font> 秒');
    } else
        timer2 = setTimeout("timedCount2()", 1000);
}

function timedReverse2() {
    var second = parseInt($('#count2').text()) - 1;
    second = second == -1 ? 0 : second;
    $('#count2').text(second);
    if (second == 0) {
        clearTimeout(timer2);
        $('#play_luyin2').attr('src', 'http://res.jian-hu.cn/static/img/bofang@2x.png');
        $('#luyin-stop2').html('');
        $('#chonglu2').html('<div class="jian-luyin-2" id="luyin-chonglu">重录</div>');
        $('#yilu_label2').html('点击播放，已录 <font style="color: #ff9600;" id="count2">' + second2 + '</font> 秒');
    } else
        timer2 = setTimeout("timedReverse2()", 1000);

}

