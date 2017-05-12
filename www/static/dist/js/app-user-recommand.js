       

var loading = false;  //状态标记
$('.weui_tab_bd').infinite();
var id = 3;
$('.weui_tab_bd').infinite().on("infinite", function () {
    if (id>5) {
        $('#load-more').html("∩_∩ 暂无更多图片")
        return
    };
    var jian_item = '<div style="width: 100%;margin-top: 10px;"><img src="http://res.jian-hu.cn/static/img/tencent'+id+'.jpg" width="100%"></div>'
    if (loading) return;
    loading = true;
    setTimeout(function () {
        id++;
        $("#img-view").append(jian_item).append(jian_item);
        loading = false;
    }, 1500);   //模拟延迟
});


$('.jian-my-luyin').on('click', function(event) {
    var _this = $(event.target);
    var img = _this.find('#play');
    // console.log(img);
    img.attr('src', 'http://res.jian-hu.cn/static/img/say@2x.gif');
});