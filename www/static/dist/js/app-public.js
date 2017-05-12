/**
 * Created by yang on 2016/8/23.
 */

$(function () {
    $('#closebt').click(function () {
        $('#jian-modal').hide();
        $('#jian-cover').hide();
    });
    $('#jian-cover').click(function () {
        $('#jian-modal').hide();
        $('#jian-cover').hide();
    });

});
function openModal(user) {
    $('#modal_user_img').attr('src', user.portrait);
    $('#name').text(user.nick);
    $('#modal_user_title').text(user.user_title);
    $('#modal_user_company').text(user.user_company);
    $('#modal_user_city').text(user.user_city);
    $('#info').text(user.user_desc);
    var vip_display = user.vip?"block":"none";
    $('#vip').css('display',vip_display);

    $('#jian-modal-portrait').css({'margin': '-30px auto','margin-bottom':'0', 'width': '40px', 'height': '40px'});
    $('#name').css({'text-align': 'center','line-height': '16px','margin-top':'16px','font-size': '16px'});
    $('#info').css({'text-align':'left','margin': '6px 8px','font-size': '13px','line-height': '16px'});
    $('#user_profile').show();

    $('#jian-modal').center();
    $('#jian-cover').show();
    $('#jian-modal').fadeIn(100, "linear");
}


function openPostJobSuccessModal(src,title,info){

    $("#vip").css("display","none");
    $('#jian-modal-portrait').css({'margin': '-10px auto', 'width': '60px', 'height': '60px'});
    $('#modal_user_img').attr('src',src);
    $('#user_profile').hide();
    $('#name').html(title).css('color', '#ff9600').css("margin-top", '14px');
    $('#info').html(info).css({'text-align':'left','margin-top':'18px'});

    $('#jian-modal').center();
    $('#jian-cover').show();
    $('#jian-modal').fadeIn(100, "linear");

    $("#jian-cover").css("opacity",'0.5');
}

jQuery.fn.center = function (loaded) {
    var obj = this;
    body_width = parseInt($(window).width());
    body_height = parseInt($(window).height());
    block_width = parseInt(obj.width());
    block_height = parseInt(obj.height());

    left_position = parseInt((body_width / 2) - (block_width / 2) + $(window).scrollLeft());
    if (body_width < block_width) {
        left_position = 0 + $(window).scrollLeft();
    }

    top_position = parseInt((body_height / 2) - (block_height / 2) + $(window).scrollTop());
    if (body_height < block_height) {
        top_position = 0 + $(window).scrollTop();
    }
    ;

    if (!loaded) {

        obj.css({
            'position': 'absolute'
        });
        obj.css({
            'top': ($(window).height() - $(obj).height()) * 0.48,
            'left': left_position
        });
        $(window).bind('resize', function () {
            obj.center(!loaded);
        });
        $(window).bind('scroll', function () {
            obj.center(!loaded);
        });

    } else {
        obj.stop();
        obj.css({
            'position': 'absolute'
        });
        obj.animate({
            'top': top_position
        }, 100, 'linear');
    }
}