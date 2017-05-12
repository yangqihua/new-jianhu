# -*- coding: utf-8 -*-
import time
import settings
from django.shortcuts import HttpResponse, render_to_response
from wx_base import handler
from wx_base.backends.dj import Helper, sns_userinfo
from wx_base import WeixinHelper, JsApi_pub, WxPayConf_pub, UnifiedOrder_pub, Notify_pub, catch
from user.models import WxSubscribe
from common.redis_clt import get_user_redis
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def wx_io(request):
    """公众平台对接"""
    if request.method == "GET":
        signature = request.GET.get("signature", "")
        timestamp = request.GET.get("timestamp", "")
        nonce = request.GET.get("nonce", "")
        if not any([signature, timestamp, nonce]) or not WeixinHelper.checkSignature(signature, timestamp, nonce):
            return HttpResponse("check failed")
        return HttpResponse(request.GET.get("echostr"))
    elif request.method == "POST":
        if settings.DEBUG:
            print "[WeiXin] Api: ", request.body
        hd = handler.MessageHandle(request.body)
        response = hd.start()
        return HttpResponse(response)
    else:
        return HttpResponse("")


@handler.subscribe
def subscribe(xml):
    openid = xml.FromUserName
    wxsubscribes = WxSubscribe.objects.filter(wx_openid=openid)[:1]
    if wxsubscribes:
        wxsubscribes[0].wx_subscribed = True
        wxsubscribes[0].save()
    else:
        wxsubscribe = WxSubscribe(wx_openid=openid, wx_subscribed=True)
        wxsubscribe.save()

    get_user_redis().delete(openid)
    return "主公来了？！荐妹妹这厢有礼了。随时听候您的差遣。"


@handler.unsubscribe
def unsubscribe(xml):
    openid = xml.FromUserName

    wxsubscribes = WxSubscribe.objects.filter(wx_openid=openid)[:1]
    if wxsubscribes:
        wxsubscribes[0].wx_subscribed = False
        wxsubscribes[0].save()

    get_user_redis().delete(openid)
    return "GoodBye"


#用户发送文本消息到服务器，我们需求进行对接多客服
@handler.text
def text(xml):
    content = xml.Content
    if content == "fulltext":
        return {"Title": "美女", "Description": "比基尼美女",
                "PicUrl": "http://9smv.com/static/mm/uploads/150411/2-150411115450247.jpg",
                "Url": "http://9smv.com/beauty/list?category=5"}
    elif content == "push":
        Helper.send_text_message(xml.FromUserName, "推送消息测试")
        return "push ok"

    return "诺！荐妹妹这就和管家商量去，再回你。"


@handler.click
def click(xml):
    return "ok"


@sns_userinfo
def oauth(request):
    """网页授权获取用户信息"""
    resp = HttpResponse(request.openid)
    resp.set_cookie("openid", Helper.sign_cookie(request.openid))
    return resp


def share(request):
    """jssdk 分享"""
    url = "http://" + request.get_host() + request.path
    sign = Helper.jsapi_sign(url)
    sign["appId"] = WxPayConf_pub.APPID
    return render_to_response("share.html", {"jsapi": sign})


@sns_userinfo
def pay(request):
    response = render_to_response("pay.html")
    response.set_cookie("openid", Helper.sign_cookie(request.openid))
    return response


@sns_userinfo
@catch
def paydetail(request):
    """获取支付信息"""
    openid = request.openid
    money = request.POST.get("money") or "0.01"
    money = int(float(money) * 100)

    jsApi = JsApi_pub()
    unifiedOrder = UnifiedOrder_pub()
    unifiedOrder.setParameter("openid", openid)  # 商品描述
    unifiedOrder.setParameter("body", "充值测试")  # 商品描述
    timeStamp = time.time()
    out_trade_no = "{0}{1}".format(WxPayConf_pub.APPID, int(timeStamp * 100))
    unifiedOrder.setParameter("out_trade_no", out_trade_no)  # 商户订单号
    unifiedOrder.setParameter("total_fee", str(money))  # 总金额
    unifiedOrder.setParameter("notify_url", WxPayConf_pub.NOTIFY_URL)  # 通知地址
    unifiedOrder.setParameter("trade_type", "JSAPI")  # 交易类型
    unifiedOrder.setParameter("attach", "6666")  # 附件数据，可分辨不同商家(string(127))
    try:
        prepay_id = unifiedOrder.getPrepayId()
        jsApi.setPrepayId(prepay_id)
        jsApiParameters = jsApi.getParameters()
    except Exception as e:
        print(e)
    else:
        print jsApiParameters
        return HttpResponse(jsApiParameters)


FAIL, SUCCESS = "FAIL", "SUCCESS"


@catch
def payback(request):
    """支付回调"""
    xml = request.raw_post_data
    # 使用通用通知接口
    notify = Notify_pub()
    notify.saveData(xml)
    print xml
    # 验证签名，并回应微信。
    # 对后台通知交互时，如果微信收到商户的应答不是成功或超时，微信认为通知失败，
    # 微信会通过一定的策略（如30分钟共8次）定期重新发起通知，
    #尽可能提高通知的成功率，但微信不保证通知最终能成功
    if not notify.checkSign():
        notify.setReturnParameter("return_code", FAIL)  #返回状态码
        notify.setReturnParameter("return_msg", "签名失败")  #返回信息
    else:
        result = notify.getData()

        if result["return_code"] == FAIL:
            notify.setReturnParameter("return_code", FAIL)
            notify.setReturnParameter("return_msg", "通信错误")
        elif result["result_code"] == FAIL:
            notify.setReturnParameter("return_code", FAIL)
            notify.setReturnParameter("return_msg", result["err_code_des"])
        else:
            notify.setReturnParameter("return_code", SUCCESS)
            out_trade_no = result["out_trade_no"]  #商户系统的订单号，与请求一致。
        ###检查订单号是否已存在,以及业务代码(业务代码注意重入问题)

    return HttpResponse(notify.returnXml())

