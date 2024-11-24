import execjs
import requests
from bs4 import BeautifulSoup
import re
import os
import pickle
postdata = {

}
_pwdDefaultEncryptSalt = ""

"""
    BHU SSO统一认证自动化
    
    声明：仅用于CAS1.0协议以及加密算法学习成果分享与交流，请勿用于非法用途，后果自负！
    Usage: 拿到了具有认证态的session还不会用？允许allow_redirects=True去访问想要的资源login即可完成服务的自认证。
    
    参考实现:https://blog.csdn.net/zhutou_xu/article/details/114212377
"""

class casService(object):
    """
    :argument svr_session:传入一个session对象即可
    :argument use_cache:使用cookie文件缓存，请了解原理后再使用!（未实现过期自动删除，需要自己判断）
    """
    def __init__(self,svr_session,use_cache=False):
        self.cas_url = ""
        self.svr_session = svr_session  #service_session
        self.session = requests.session() #cas session
        self.use_cache = use_cache
        if use_cache:
            self.load_cascookies_from_file() #使用已有的cas-cookie(如果有的话)
        self.headers = {
              "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
              "Accept-Language": "zh_CN",
              "Connection": "keep-alive",
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363",
             }
    def Login(self,serviceUrl = "",username = None,password = None):
        global _pwdDefaultEncryptSalt
        global postdata
        response = self.svr_session.get(url=serviceUrl,allow_redirects=False, verify=False)
        if response.status_code == 200:            
            return True
        self.cas_url = response.headers["Location"]

        cas_response = self.session.get(self.cas_url,allow_redirects = False, verify=False)
        print(cas_response.text)
        if cas_response.status_code == 200:#登录界面
            if username == None or password == None:
                print("cas_cookie not valid")
                username = input("plase input username:")
                password = input("plase input password:")
            self.cas_url = response.headers["location"]
            js_code = open("encrypt.js", "r", encoding="utf-8").read()
            js_ctx = execjs.compile(js_code)
            # 正则表达式，用于匹配变量定义和它的值
            regex = r'var\s+pwdDefaultEncryptSalt\s*=\s*"([^"]+)";'
            # 使用正则表达式进行匹配
            match = re.search(regex, cas_response.text)

            if match:
                pwdDefaultEncryptSalt = match.group(1)
                _pwdDefaultEncryptSalt = pwdDefaultEncryptSalt
                print("提取出的pwdDefaultEncryptSalt值是:", pwdDefaultEncryptSalt)
            else:
                print("未找到pwdDefaultEncryptSalt变量")
            encryptPassword = js_ctx.call("encryptAES", password, str(_pwdDefaultEncryptSalt))

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(cas_response.text, 'html.parser')

            # 查找表单
            form = soup.find('form', id='casLoginForm')

            # 提取具有name属性的input元素
            inputs = form.find_all('input', attrs={'name': True})

            # 打印name属性和值
            for input_element in inputs:
                name = input_element.get('name')
                value = input_element.get('value')
                print(f"name: {name}, value: {value}")
                if value == None:
                    continue
                postdata[name] = value

            postdata["username"]=username
            postdata["password"]=encryptPassword
            auth_response = self.session.post(self.cas_url,data = postdata,allow_redirects = False, verify=False)
            if auth_response.status_code == 302:
                url_with_ticket = auth_response.headers["location"]
                confirm_response = self.svr_session.get(url = url_with_ticket,allow_redirects = True, verify=False)
                if confirm_response.status_code == 200:
                    print("logon on success")
                    print(self.session.cookies)
                    self.write_cascookies_to_file()
                    return True
                else:
                    print("logon on failed")
            else:
                print('auth failed')
                return False  
        else:
            print("cas cookies still valid")
            url_with_ticket = cas_response.headers["location"]
            confirm_response = self.svr_session.get(url = url_with_ticket,allow_redirects = True, verify=False)
            if confirm_response.status_code == 200:
                print("nopassword login success")
                return True
            else:
                print("cas url_with_ticket error")
                return False

    def load_cascookies_from_file(self):
        if os.path.exists("cas_cookies.dat"):
            with open("cas_cookies.dat", 'rb') as f:
                self.session.cookies.update(pickle.load(f))
    def write_cascookies_to_file(self):
        if self.use_cache is False:
            return
        with open("cas_cookies.dat",'wb') as f:
            pickle.dump(self.session.cookies,f)

