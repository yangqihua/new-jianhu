
$('.collection-job').on('click', function(event) {
    var _this = $(event.target);
    console.log(_this);
    location.href = "/user/collection_detail";
});        

item_count = $('.jian_list_items').children().length/2;
if(item_count>=5){        //元素个数大于这个值才启用滚到加载组件
    var loading = false;  //状态标记
    $('.weui_tab_bd').infinite();
    // $('.weui_tab_bd').destroyInfinite();
    $('.weui_tab_bd').infinite().on("infinite", function () {
        console.log("okk");
        var jian_item = '<div class="jian-item-space"></div><div class="jian-item-title"><div><font class="jian-item-title-font">高级UED工程师</font></div><div class="weui-row weui-no-gutter jian-item-content"><div class="weui-col-50"><div class="weui-row weui-no-gutter"><div class="weui-col-50"><div style="float: left"><img class="jian-item-content-img" src="http://res.jian-hu.cn/static/img/icn_place@2x.png"><font class="jian-item-content-fontyahei">北京</font></div></div><div class="weui-col-50"><div style="margin-left: 10px;"><img src="http://res.jian-hu.cn/static/img/icn_time@2x.png" class="jian-item-content-img"><font class="jian-item-content-fontyahei">3-5年</font></div></div></div></div><div class="weui-col-50"><div class="weui-row weui-no-gutter"><div class="weui-col-50"><div style="margin-left: 15px;"><img src="http://res.jian-hu.cn/static/img/icn_xueli@2x.png" class="jian-item-content-img"><font class="jian-item-content-fontyahei">本科</font></div></div><div class="weui-col-50"><div style="float: right"><!-- <img src="http://res.jian-hu.cn/static/img/yuan@2x.png" class="jian-item-content-img"> --><font class="jian-item-content-fontxinzi">￥10k-15k</font></div></div></div></div></div><div class="weui-row weui-no-gutter jian-item-me"><div class="weui-col-33"><div style="float: left"><img src="http://res.jian-hu.cn/static/img/default.jpg" class="jian-item-me-img"><font class="jian-item-me-fontname">我的发布</font></div></div><div class="weui-col-33" style="text-align: center"><font class="jian-item-me-fontcompany">深圳腾讯有限公司</font></div><div class="weui-col-33" style="text-align: right"><font class="jian-item-me-fontcompany">三小时前发布</font></div></div></div>';

        if (loading) return;
        loading = true;
        setTimeout(function () {
            $(".jian_list_items").append(jian_item).append(jian_item).append(jian_item);
            loading = false;
        }, 1500);   //模拟延迟
    });
}else{
    $('.weui-infinite-scroll').css('display', 'none');
}