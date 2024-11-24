from requests import Session


import argparse

from cas_service import casService
from util import replace_value_in_config, backup_file


def getCookie(username,password):
    # 创建一个服务会话对象
    svr_session = Session()

    server = casService(svr_session)

    server.Login("https://webvpn.beihua.edu.cn/login", username=username, password=password)
    resp = server.session.get(url='https://webvpn.beihua.edu.cn/login', allow_redirects=True)
    needCookie = ""
    if resp.status_code == 302:
        print("如果使用了文件缓存模式，请删除文件，认证已经过期!\n")
        print("如果没有使用，请检查是否进行了Login!\n")
    if resp.status_code == 200:
        # print(resp.text)
        resp = server.session.get(url='https://webvpn.beihua.edu.cn', allow_redirects=True)
        needCookie = server.session.cookies.get("wengine_vpn_ticketwebvpn_beihua_edu_cn", None, ".webvpn.beihua.edu.cn",
                                                "/")
        print("请勿泄露webvpnCookie:" + needCookie)
        return needCookie
    return ""

def updateYaml(config_path,cookie):
    if cookie == None or cookie == "":
        raise "错误的cookie"
    key_to_replace = 'wengine_vpn_ticketwebvpn_beihua_edu_cn'
    new_value = cookie

    # 备份文件
    backup_path = backup_file(config_path)
    print(f"备份文件已创建: {backup_path}")

    # 替换值
    replace_value_in_config(config_path, key_to_replace, new_value)
    print(f"已将 {key_to_replace} 的值替换为 {new_value}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='此代码用于求两个整数之和')
    parser.add_argument("username", type=str, help="用户名")
    parser.add_argument("password",type=str,help="用户的密码")
    parser.add_argument("config_path",type=str,help="clash配置文件的完整位置（例如/etc/mihomo/config.yaml）")
    args = parser.parse_args()
    if args.config_path == None or args.config_path == "":
        parser.print_help()
        exit(0)
    cookie = getCookie(args.username,args.password)
    if cookie == None or cookie == "":
        raise "异常的cookie"
        exit(0)
    updateYaml(args.config_path,cookie)
