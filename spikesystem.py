# pyinstaller spikesystem.py -F -w -i 1.ico
import datetime
import os
import threading
import time
import tkinter
from _datetime import datetime as acquisition_time  # 不同模块取别名
from re import compile
from time import sleep
from tkinter import *
from tkinter import font
from tkinter import messagebox

import ntplib
import pyautogui as pyautogui
from selenium import webdriver  # 导入webdriver模块
from selenium.common.exceptions import WebDriverException, NoSuchElementException, InvalidSessionIdException
from selenium.webdriver.chrome.options import Options as chromeOptions
from selenium.webdriver.chrome.service import Service as chromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as edgeOptions
from selenium.webdriver.edge.service import Service as edgeService
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.firefox.service import Service as firefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# 服务器对时
def verify_ntp_time(time_server):
    count = 0
    while True:
        try:
            response = ntplib.NTPClient().request(time_server)
            ts = response.tx_time
            _date = time.strftime('%Y-%m-%d', time.localtime(ts))
            _time = time.strftime('%X', time.localtime(ts))
            os.system('date {} && time {}'.format(_date, _time))
            t1 = time.strftime('%Y-%m-%d %X', time.localtime(ts))
            t2 = datetime.datetime.now().strftime('%Y-%m-%d %X')
            if count == 2:  # 防止对时死循环
                return False
            if t1 == t2:
                return True
            else:
                count += 1
        except Exception:
            pass


# 对时国家授时中心
def ntp_timing_china():
    return verify_ntp_time('ntp.api.bz')


# 对时阿里云NTP服务器
def ntp_timing_aliyun():
    return verify_ntp_time('ntp.aliyun.com')


# 时间自动优化
def cause_time():
    compare_month = [4, 6, 9, 11]  # 只有30天的月份
    now_time = list(acquisition_time.now().strftime("%Y-%m-%d %H:%M:%S"))  # 把当前时间转成列表
    now_time[14:19] = '00:00'  # 把时间变为整时
    hour = int(''.join(now_time[11:13])) + 1
    year = int(''.join(now_time[0:4]))
    now_time[11:13] = str(hour)
    if hour < 10:
        now_time.insert(11, '0')
    if hour == 24:
        now_time[11:13] = '00'
        day = int(''.join(now_time[8:10]))
        global month
        month = int(''.join(now_time[5:7]))
        if day == 28:
            leap_year = 2020
            while True:
                leap_year = leap_year + 4
                if year == leap_year:
                    if month == 2:
                        now_time[8:10] = '29'
                        break
                elif leap_year < year:
                    continue
                else:
                    if month == 2:
                        now_time[8:10] = '01'
                        now_time[5:7] = str(month + 1)
                        if month < 10:
                            now_time.insert(5, '0')
                            day = 0
                if leap_year > year:
                    break
        elif day == 29:
            if month == 2:
                now_time[8:10] = '01'
                now_time[5:7] = str(month + 1)
                now_time.insert(5, '0')
                month = month + 1
                day = 0
        elif day == 30:
            for i in compare_month:
                if month == i:
                    now_time[8:10] = '01'
                    now_time[5:7] = str(month + 1)
                    if month < 10:
                        now_time.insert(5, '0')
                        day = 0
                    break
        elif day == 31:
            now_time[8:10] = '01'
            now_time[5:7] = str(month + 1)
            if month < 10:
                now_time.insert(5, '0')
                day = 0
            if month == 12:
                now_time[5:7] = '01'
                now_time[0:4] = str(year + 1)
        if day + 1 == 32:
            now_time[8:10] = '01'
        else:
            now_time[8:10] = str(day + 1)
            if day < 9:
                now_time.insert(8, '0')
    now_time = ''.join(now_time)
    return now_time


def limit_password(data):
    # 如果不加上==""的话,就会发现删不完。总会剩下一个数字 isdigit函数：isdigit函数方法检测字符串是否只由数字组成。
    if (data.isdigit() and len(data) <= 6) or data == "":
        return True
    else:
        return False


class SpikeSystem(object):
    # 启动程序
    def __init__(self):
        self.options = None
        self.path = None  # 浏览器选择
        self.thread = None  # 多线程
        self.driver = None  # 驱动
        self.choice = None  # 购物车选择
        self.url_path = None  # 网址
        self.buy_time = None  # 秒杀时间
        self.password = None  # 支付密码
        self.time_remaining = datetime.timedelta(seconds=6)
        self.window = Tk()  # 建立窗口window
        self.window.title('秒杀系统4.1(作者:Kearns201)')  # 窗口名称
        # 窗口大小参数(宽＊高)
        width = 610
        height = 320
        # 获取屏幕大小并计算起始坐标
        screen_width = (self.window.winfo_screenwidth() - width) / 2
        screen_height = (self.window.winfo_screenheight() - height) / 2
        # 设置窗口大小以及位置
        self.window.geometry(f'{width}x{height}+{int(screen_width)}+{int(screen_height)}')
        # 控制窗口大小不可更改
        self.window.resizable(False, False)
        # 创建菜单栏
        self.bar = Menu()
        # # 创建菜单
        self.url_shop = Menu(self.bar, tearoff=0)  # 第二个参数是指去掉菜单和菜单栏之间的横线
        self.url_phone = Menu(self.bar, tearoff=0)
        self.buy_car = Menu(self.bar, tearoff=0)
        self.choice_browser = Menu(self.bar, tearoff=0)
        self.ntp_time = Menu(self.bar, tearoff=0)
        # # 将菜单添加到菜单栏中,并添加标签
        self.bar.add_cascade(label='选择网站(电商)', font=font.Font(size=12), menu=self.url_shop)
        self.bar.add_cascade(label='选择网站(手机)', font=font.Font(size=12), menu=self.url_phone)
        self.bar.add_cascade(label='是否全选购物车', font=font.Font(size=12), menu=self.buy_car)
        self.bar.add_cascade(label='选择浏览器', font=font.Font(size=12), menu=self.choice_browser)
        self.bar.add_cascade(label='NTP对时', font=font.Font(size=12), menu=self.ntp_time)
        # 给关于菜单添加菜单栏
        # 选择网站(电商)
        self.url_shop.add_command(label='淘宝', font=font.Font(size=10), command=self.url_taobao)
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='京东', font=font.Font(size=10), command=self.url_jd)
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='苏宁', font=font.Font(size=10), command=self.url_suning)
        # 选择网站(手机)
        self.url_phone.add_command(label='vivo', font=font.Font(size=10), command=self.url_vivo)
        self.url_phone.add_separator()  # 分割线
        self.url_phone.add_command(label='oppo', font=font.Font(size=10), command=self.url_oppo)
        self.url_phone.add_separator()
        self.url_phone.add_command(label='小米', font=font.Font(size=10), command=self.url_xiaomi)
        self.url_phone.add_separator()
        self.url_phone.add_command(label='华为', font=font.Font(size=10), command=self.url_huawei)
        # 购物车选择
        self.buy_car.add_command(label='自动全选', font=font.Font(size=10), command=self.check_all)
        self.buy_car.add_separator()  # 分割线
        self.buy_car.add_command(label='手动单选', font=font.Font(size=10), command=self.check_multiple)
        # 浏览器选择栏
        self.choice_browser.add_command(label='Edge浏览器', font=font.Font(size=10), command=self.browser_edge)
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='谷歌浏览器', font=font.Font(size=10), command=self.browser_chrome)
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='火狐浏览器', font=font.Font(size=10), command=self.browser_firefox)
        # 手动NTP对时
        self.ntp_time.add_command(label='国家授时中心', font=font.Font(size=10), command=ntp_timing_china)
        self.ntp_time.add_separator()  # 分割线
        self.ntp_time.add_command(label='阿里云', font=font.Font(size=10), command=ntp_timing_aliyun)
        # 将菜单栏放入主窗口
        self.window.config(menu=self.bar)
        # 容器1
        self.frame1 = Frame(self.window, bd=8)
        self.label_buy_time = Label(self.frame1, width=100, height=2, bg='#FC1944', bd=5, relief=RIDGE,
                                    font=font.Font(size=12))
        self.label_buy_time['text'] = '请输入秒杀/抢购时间(格式:2000-01-01 20:00:00)'
        self.label_buy_time.pack()
        self.text_time = tkinter.StringVar(value=cause_time())
        self.buy_time_entry = Entry(self.frame1, width=100, bd=5, justify=CENTER,
                                    textvariable=self.text_time  # 文本框的值,是一个StringVar()对象,这样与StringVar就能更新
                                    # 跟踪变量的值的变化,以保证值的变更随时可以显示在界面上
                                    )  # 文本输入框
        self.buy_time_entry.pack()  # 把text放在window上面,显示text这个控件
        self.frame1.pack()
        # 容器2
        self.frame2 = Frame(self.window, bd=8)
        self.label_password = Label(self.frame2, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                    font=font.Font(size=12))
        self.label_password['text'] = '请输入支付密码(仅做自动填充,手动输入请留空)'
        self.label_password.pack()
        # 端口input
        password = self.window.register(limit_password)  # 需要将函数包装一下,必要的, 否则会直接调用
        self.password_entry = Entry(self.frame2,  # 置入容器
                                    width=100, bd=5,
                                    justify=CENTER,  # 居中对齐显示
                                    show='*',  # 显示加密
                                    textvariable=StringVar(),  # 文本框的值,是一个StringVar()对象,这样与StringVar 就能更新
                                    # 跟踪变量的值的变化,以保证值的变更随时可以显示在界面上
                                    validate="key",
                                    # 发生任何变动的时候,就会调用validate-command 这个调动受后面'Key'影响,类似键盘监听 如果换成"focusout"就是光标
                                    validatecommand=(password, '%P'))  # %P代表输入框的实时内容 # %P表示 当输入框的值允许改变,该值有效。
        # 该值为当前文本框内容 # %v(小写大写不一样的),当前validate的值  # %W表示该组件的名字)  # 文本输入框
        self.password_entry.pack()  # 把text放在window上面,显示text这个控件
        self.frame2.pack()
        self.frame1.columnconfigure(1, weight=1)
        self.frame1.rowconfigure(0, weight=1)
        self.frame2.columnconfigure(1, weight=1)
        self.frame2.rowconfigure(0, weight=1)
        # 确定按钮
        self.button = Button(self.window, height=2, width=20, text="确定", bg='#FC5531', bd=8,
                             command=self.getparms)
        self.button.pack()  # 显示按钮

    # 网址选择
    def url_taobao(self):  # 选择淘宝
        self.url_path = 'https://login.taobao.com/'
        ntp_timing_china()

    def url_jd(self):  # 选择京东
        self.url_path = 'https://passport.jd.com/new/login.aspx'
        ntp_timing_china()

    def url_suning(self):  # 选择苏宁易购
        self.url_path = 'https://passport.suning.com/ids/login'
        ntp_timing_china()

    def url_vivo(self):  # 选择vivo
        self.url_path = 'https://passport.vivo.com.cn/#/login'
        ntp_timing_china()

    def url_oppo(self):  # 选择oppo
        self.url_path = 'https://id.oppo.com/index.html'
        ntp_timing_china()

    def url_xiaomi(self):  # 选择小米
        self.url_path = 'https://account.xiaomi.com/fe/service/login/password'
        ntp_timing_china()

    def url_huawei(self):  # 选择华为
        self.url_path = 'https://id1.cloud.huawei.com/CAS/portal/loginAuth.html'

    # 购物车选择
    def check_all(self):  # 全选购物车
        self.choice = 'check_all'

    def check_multiple(self):  # 手动单选购物车
        self.choice = 'untick'

    # 浏览器选择
    def browser_edge(self):  # 选择edge浏览器
        self.path = 'edge'

    def browser_chrome(self):  # 选择谷歌浏览器
        self.path = 'chrome'

    def browser_firefox(self):  # 选择火狐浏览器
        self.path = 'firefox'

    # 多线程
    def add_thread(self):
        # 判断是否有线程在运行
        if self.thread is not None:
            messagebox.showinfo('提示', '参数已更新\n点击确定重新调用程序')
            try:
                self.driver.quit()
            except AttributeError:
                pass
            finally:
                # 如果线程已经运行就停止并重新以当前属性开启一个新线程
                self.thread = threading.Thread(target=self.main)
                self.thread.daemon = True
                self.thread.start()
        else:
            # 如果没有运行就开启一个新线程
            self.thread = threading.Thread(target=self.main)
            self.thread.daemon = True
            self.thread.start()

    # 获取参数
    def getparms(self):
        acquisition_time_format = compile(
            '^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))\s(([1-9])|([0-1][0-9])|([1-2][0-3])):([0-5][0-9]):([0-5][0-9])$')
        buy_time = self.buy_time_entry.get()
        self.password = self.password_entry.get()
        if self.url_path is None:
            messagebox.showinfo(title='提示', message='请选择网站')
            return
        elif self.choice is None:
            messagebox.showinfo(title='提示', message='请选择是否全选购物车')
            return
        elif self.path is None:
            messagebox.showinfo(title='提示', message='请选择浏览器')
            return
        elif not buy_time:
            messagebox.showinfo(title='提示', message='请输入秒杀时间')
            return
        elif acquisition_time_format.match(buy_time) is None:
            messagebox.showwarning(title='警告', message='格式错误\n请检查并输入正确的抢购时间')
            return
        self.buy_time = acquisition_time.strptime(buy_time, '%Y-%m-%d %H:%M:%S')
        self.add_thread()

    # 秒杀主程序
    def main(self):
        self.driver = self.drivers()  # 指定浏览器驱动
        try:
            if self.driver is None:
                return False
            else:
                # 全屏化页面
                self.driver.maximize_window()
                if self.url_path == 'https://login.taobao.com/':
                    self.taobao()  # 淘宝
                if self.url_path == 'https://passport.jd.com/new/login.aspx':
                    self.jd()  # 京东
                if self.url_path == 'https://passport.suning.com/ids/login':
                    self.suning()  # 苏宁
                if self.url_path == 'https://passport.vivo.com.cn/#/login':
                    self.vivo()  # vivo
                if self.url_path == 'https://id.oppo.com/index.html':
                    self.oppo()
                if self.url_path == 'https://account.xiaomi.com/fe/service/login/password':
                    self.xiaomi()
                if self.url_path == 'https://id1.cloud.huawei.com/CAS/portal/loginAuth.html':
                    self.huawei()
                self.quit()  # 销毁主窗口
        except InvalidSessionIdException:
            return False
        except WebDriverException:
            return False

    # 销毁主窗口
    def quit(self):
        self.window.destroy()

    # 浏览器驱动函数
    def drivers(self):
        self.driver = self.online_driver()
        return self.driver  # 返回浏览器驱动程序

    # 调用在线驱动
    def online_driver(self):
        online_driver = None
        browser_service = {'edge': edgeService, 'chrome': chromeService, 'firefox': firefoxService}  # 新特性service容器
        browser = {'edge': webdriver.Edge, 'chrome': webdriver.Chrome, 'firefox': webdriver.Firefox}  # 选择浏览器
        if self.path == 'edge':
            online_driver = EdgeChromiumDriverManager().install()
            self.options = edgeOptions()
        elif self.path == 'chrome':
            online_driver = ChromeDriverManager().install()
            self.options = chromeOptions()
        elif self.path == 'firefox':
            online_driver = GeckoDriverManager().install()
            self.options = firefoxOptions()
        try:
            self.options.add_argument("--disable-blink-features")
            self.options.add_argument("--disable-blink-features=AutomationControlled")
            service = browser_service[self.path](online_driver)  # service容器
            self.driver = browser[self.path](service=service, options=self.options)  # 启动浏览器驱动
        except WebDriverException:
            messagebox.showerror(title='错误:启动失败', message='请确认是否安装了相应的浏览器')
        return self.driver

    # 登录函数
    def login(self, detection, url, qr=None):
        """
        :param detection: 传入当前页面存在的元素Xpath,用以检测是否离开当前页面
        :param url: 要跳转的购物车链接地址
        :param qr: 默认为空,如果默认没有展示二维码,则可以传入二维码的Xpath
        :return: 布尔值
        """
        self.driver.get(self.url_path)
        sleep(5)
        if qr is None:
            pass
        else:
            while True:
                try:
                    if self.driver.find_element(By.XPATH, qr):
                        self.driver.find_element(By.XPATH, qr).click()
                        break
                except NoSuchElementException:
                    pass
                except Exception:
                    return False
        while True:
            try:
                if self.driver.find_element(By.XPATH, detection).is_displayed():
                    sleep(1)
            except NoSuchElementException:
                self.driver.get(url)
                break
            except Exception:
                return False

    # 全选函数
    def check(self, check_box, check_login=None):
        """
        :param check_box: 传入全选框的Xpath
        :param check_login: 默认值为空, 传入购物车页面需要二次点击登录刷新cookie
        :return: 布尔值
        """
        if check_login is None:
            pass
        else:
            while True:
                try:
                    # 全选购物车
                    self.driver.find_element(By.XPATH, check_login).click()
                    break
                except NoSuchElementException:
                    sleep(1)
                except Exception:
                    return False
        if self.choice == 'check_all':
            while True:
                try:
                    # 全选购物车
                    self.driver.find_element(By.XPATH, check_box).click()
                    break
                except NoSuchElementException:
                    sleep(1)
                except Exception:
                    return False
        else:
            pass

    # 秒杀函数
    def seckill(self, settlement, submit):
        """
        :param settlement: 传入购物车页面的结算按钮Xpath
        :param submit: 传入地址确认页面的提交按钮Xpath
        :return: 布尔值
        """
        # 循环对比时间
        while True:
            # 获取当前时间
            now_time = acquisition_time.now()
            # 判断当前时间是否大于设定时间
            if now_time >= self.buy_time:
                # 如果大于设定时间,则点击购买按钮
                try:
                    self.driver.find_element(By.XPATH, settlement).click()
                    break
                except NoSuchElementException:
                    pass
                except Exception:
                    return False
            if (self.buy_time - now_time) > self.time_remaining:
                sleep(4.5)
        while True:
            try:
                # 循环点击提交按钮
                self.driver.find_element(By.XPATH, submit).click()
                break
            except NoSuchElementException:
                pass
            except Exception:
                return False

    # 付款函数
    def pay(self, input_box, ensure=None, click_to_pay=None):
        """
        :param input_box: 传入密码输入框Xpath
        :param ensure: 默认为空,传入确认付款按钮Xpath
        :param click_to_pay: 默认为空,传入点击去付款调出输入框按钮Xpath
        :return: 布尔值
        """
        if click_to_pay is None:
            pass
        else:
            # 循环点击支付按钮
            while True:
                try:
                    self.driver.find_element(By.XPATH, click_to_pay).click()
                    break
                except NoSuchElementException:
                    sleep(1)
                except Exception:
                    return False
        if self.password is not None and self.password.isspace() is False and self.password.isnumeric() and len(
                self.password) == 6:
            while True:
                sleep(1)
                try:
                    # 判断是否有输入框
                    if self.driver.find_element(By.XPATH, input_box):
                        for i in range(len(self.password)):
                            pyautogui.press(self.password[i])
                        sleep(0.5)
                        if ensure is None:
                            pyautogui.press('enter')
                        else:
                            self.driver.find_element(By.XPATH, ensure).click()
                        sleep(8)
                        self.driver.quit()  # 退出浏览器函数
                        break
                except NoSuchElementException:
                    pass
                except Exception:
                    return False
        else:
            pass

    # 淘宝函数
    def taobao(self):
        self.login('//*[@id="header"]/div/div/a[2]', 'https://cart.taobao.com/cart.htm',
                   '//*[@id="login"]/div[1]/i')
        self.check('//*[@id="J_SelectAll1"]/div/label')
        self.seckill('//*[@id="J_Go"]', '//*[@id="submitOrderPC_1"]/div[1]/a[2]')
        self.pay('//*[@id="payPassword_container"]/div')

    # 京东函数
    def jd(self):
        self.login('//*[@id="content"]/div[2]/div[1]/div/div[5]/div/div[2]/div[1]/img',
                   'https://cart.jd.com/cart_index')
        self.check('//*[@id="cart-body"]/div[2]/div[3]/div[1]/div/input')
        self.seckill(
            '//*[@id="cart-body"]/div[2]/div[16]/div/div[2]/div/div/div/div[2]/div[2]/div/div[1]/a/b',
            '//*[@id="order-submit"]')
        self.pay('//*[@id="validateShortFake"]', '//*[@id="baseMode"]/div/div[2]/div/div[2]/div/div/div[1]',
                 '//*[@id="indexBlurId"]/div/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/div/div[1]')

    # 苏宁函数
    def suning(self):
        self.login('//*[@id="LOGIN_ADVISE"]', 'https://shopping.suning.com/cart.do#resize:380,450')
        self.check('//*[@id="chooseAllCheckFrame2"]', '//*[@id="cart-body"]/div/h2/a')
        self.seckill('//*[@id="cart-wrapper"]/div[3]/div/div/div[2]/div[2]/a', '//*[@id="submit-btn"]')

    # vivo函数
    def vivo(self):
        self.login('/html/body/div[1]/div[3]/div[1]/div/div[1]/a', 'https://shop.vivo.com.cn/shoppingcart',
                   '/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/img[2]')
        self.check('//*[@id="fixed-bottom-bar"]/div/div/div[1]/ul/li[1]/label/a')
        self.seckill('//*[@id="fixed-bottom-bar"]/div/div/div[2]/table/tr/td[2]/button', 'btn-submit')

    # oppo函数
    def oppo(self):
        self.login('//*[@id="root"]/div/div[3]/div/div[1]/div[1]', 'https://www.opposhop.cn/cn/web/cart',
                   '//*[@id="root"]/div/div[3]/div/div[2]/div/div[1]/div[2]')
        self.check('//*[@id="input-35"]')
        self.seckill('//*[@id="app"]/div/div[1]/main/div/div[2]/div/div[1]/div[3]/button',
                     '//*[@id="app"]/div/div[1]/div/main/div/div[8]/div/div/div[3]/button')

    # 小米函数
    def xiaomi(self):
        self.login('//*[@id="root"]/div/div/div[2]/div/div/div[1]/div[1]', 'https://www.mi.com/shop/buy/cart',
                   '//*[@id="root"]/div/div/div[2]/div/div/div[2]/div/div[1]/div[1]')
        self.check('//*[@id="app"]/div[2]/div/div/div/div[1]/div[2]/div[1]/div[1]/i',
                   '//*[@id="app"]/div[2]/div/div/div/div/div[1]/a[1]')
        # //*[@id="stat_e3c9df7196008778"]/div[2]/div[2]/div/div/div/div[3]/button[1]
        self.seckill('//*[@id="app"]/div[2]/div/div/div/div[1]/div[4]/span/a',
                     '//*[@id="app"]/div[2]/div/div/div[2]/div/div[6]/div/div/a[1]')

    # 华为函数
    def huawei(self):
        self.login('/html/body/div/div/div[1]/div[3]/div[2]/span/span', 'https://www.vmall.com/cart', )
        self.check('//*[@id="app"]/div[2]/div[3]/div[4]/div/div[1]/label/input',
                   '//*[@id="app"]/div[2]/div[3]/div[1]/a')
        self.seckill('//*[@id="app"]/div[2]/div[3]/div[4]/div/div[2]/a', '//*[@id="checkoutSubmit"]')


if __name__ == '__main__':
    # 实例化对象
    # messagebox.showinfo('使用说明', '请依次选择网站, 购物车, 浏览器, NTP一般不用选择, 在每次选择网站的适合都会自动对时, 正因如此, 有时候程序会响应3-5秒左右, '
    #                                 '因为国家授时中心对时协议特殊导致的, 密码无需担心泄露, 软件密文加密, 输入仅用于无人值守时全自动化抢购, '
    #                                 '如若不放心可以稍后抢购成功后手动输入')
    Spike = SpikeSystem().window
    Spike.mainloop()  # 显示窗口
