       


$('.recommand-job').on('click', function(event) {
    var _this = $(event.target);
    location.href = "/user/recommand_detail";
});

$('#collection-job').on('click', function(event) {
    var _this = $(event.target);
    console.log(_this);
    location.href = "/user/collection_detail";
});