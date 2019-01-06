# -*- coding: utf-8 -*-
from selenium import webdriver
from pickle import dump, load
from os.path import exists

COOKIE_FILE = 'data/cookies.pkl'


# Get cookies using selenium.
def get_cookies():
    try:
        browser = webdriver.Chrome(executable_path='driver/chromedriver')
        browser.get("https://www.zhihu.com/signin?next=%2F")
        # 扫码登录
        browser.execute_script("document.getElementsByTagName('Button')[8].click()")
        _ = input('请扫码登录后，再输入回车：')
        cookies = browser.get_cookies()
        dump(cookies, open(COOKIE_FILE, "wb"))
        browser.close()
        return cookies
    except Exception:
        print('当前运行环境可能缺少geckodriver，请安装geckodriver（可在项目内driver文件夹下找到）后，再尝试运行')
        print('当然，也有可能是未知错误导致页面关闭')
        exit(1)


# Load cookies.
def load_cookies():
    cookies = load(open(COOKIE_FILE, "rb")) if exists(COOKIE_FILE) else get_cookies()
    return {cookie['name']: cookie['value'] for cookie in cookies}


if __name__ == '__main__':
    print(load_cookies())
