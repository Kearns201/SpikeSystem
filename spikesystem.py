# pyinstaller spikesystem.py -F -w -i 1.ico
import datetime
import os
import socket
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
import requests.exceptions
from selenium import webdriver  # 导入webdriver模块
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as chromeOptions
from selenium.webdriver.chrome.service import Service as chromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as edgeOptions
from selenium.webdriver.edge.service import Service as edgeService
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.firefox.service import Service as firefoxService
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class SpikeSystem_window(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    # 网址选择
    def url(self, url):
        self.url_path = url
        self.ntp_timing_aliyun('auto')

    # 购物车选择
    def primary(self, choice):
        self.product_selection = choice

    # 浏览器选择
    def browser_choice(self, browser):
        self.browser = browser

    def verify_ntp_time(self, time_server, mode):
        try:
            response = ntplib.NTPClient().request(time_server)
            ts = response.tx_time
            _date = time.strftime('%Y-%m-%d', time.localtime(ts))
            _time = time.strftime('%X', time.localtime(ts))
            os.system('date {} && time {}'.format(_date, _time))
            ntp = time.strftime('%Y-%m-%d %X', time.localtime(ts))
            local = datetime.datetime.now().strftime('%Y-%m-%d %X')
            if mode == 'auto':
                if ntp == local:
                    messagebox.showinfo('提示', '自动对时成功')
            else:
                if ntp == local:
                    messagebox.showinfo('提示', '手动对时成功')
        except socket.gaierror:
            messagebox.showerror('错误', '对时失败\n请检查网络连接后再手动对时')
            return False
        except ntplib.NTPException:
            messagebox.showwarning('警告', '对时失败\n时间服务器无响应\n请手动NTP对时或选择其他NTP服务器')
            return False

    # 对时国家授时中心
    def ntp_timing_china(self, mode='manual'):
        self.verify_ntp_time('ntp.api.bz', mode)

    # 对时阿里云NTP服务器
    def ntp_timing_aliyun(self, mode='manual'):
        self.verify_ntp_time('ntp.aliyun.com', mode)

    # 时间自动优化
    def cause_time(self):
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

    # 密码限制
    def limit_password(self, data):
        # 如果不加上==""的话,就会发现删不完。总会剩下一个数字 isdigit函数：isdigit函数方法检测字符串是否只由数字组成。
        if (data.isdigit() and len(data) <= 6) or data == "":
            return True
        else:
            return False


class StartPage(Frame, SpikeSystem_window):
    def __init__(self, window):
        Frame.__init__(self, window)
        self.window = window  # 建立窗口window
        self.window.title('选择登录方式')  # 窗口名称
        # 窗口大小参数(宽＊高)
        width = 350
        height = 150
        # 获取屏幕大小并计算起始坐标
        screen_width = (self.window.winfo_screenwidth() - width) / 2
        screen_height = (self.window.winfo_screenheight() - height) / 2
        # 设置窗口大小以及位置
        self.window.geometry(f'{width}x{height}+{int(screen_width)}+{int(screen_height)}')
        # 控制窗口大小不可更改
        self.window.resizable(False, False)
        Button(self, text="扫码登录", height=2, width=20, bg='#FC5531', bd=8,
               command=lambda: self.window.switch_frame(QR_code)).pack()
        Button(self, text="账号登录", height=2, width=20, bg='#FC5531', bd=8,
               command=lambda: self.window.switch_frame(Account_login)).pack()


class QR_code(Frame, SpikeSystem_window):
    # 启动程序
    def __init__(self, window):
        Frame.__init__(self, window)
        self.browser = 'edge'  # 浏览器选择
        self.login_selection = 'qr_code'  # 登录方式选择
        self.product_selection = 'check_all'  # 购物车选择
        self.url_path = None  # 网址
        self.buy_time = None  # 秒杀时间
        self.password = None  # 支付密码
        self.window = window  # 建立窗口window
        self.window.title('秒杀系统4.1(作者:Kearns201)')  # 窗口名称
        width = 620
        height = 260
        # 获取屏幕大小并计算起始坐标
        screen_width = (self.window.winfo_screenwidth() - width) / 2
        screen_height = (self.window.winfo_screenheight() - height) / 2
        # 设置窗口大小以及位置
        self.window.geometry(f'{width}x{height}+{int(screen_width)}+{int(screen_height)}')
        # 控制窗口大小不可更改
        self.window.resizable(False, False)
        # 创建菜单栏
        self.menu = Menu()
        # # 创建菜单
        self.url_shop = Menu(self.menu, tearoff=0)  # 第二个参数是指去掉菜单和菜单栏之间的横线
        self.url_phone = Menu(self.menu, tearoff=0)
        self.buy_car = Menu(self.menu, tearoff=0)
        self.choice_browser = Menu(self.menu, tearoff=0)
        self.ntp_time = Menu(self.menu, tearoff=0)
        # # 将菜单添加到菜单栏中,并添加标签
        self.menu.add_cascade(label='选择网站(电商)', font=font.Font(size=12), menu=self.url_shop)
        self.menu.add_cascade(label='选择网站(手机)', font=font.Font(size=12), menu=self.url_phone)
        self.menu.add_cascade(label='是否全选购物车', font=font.Font(size=12), menu=self.buy_car)
        self.menu.add_cascade(label='选择浏览器', font=font.Font(size=12), menu=self.choice_browser)
        self.menu.add_cascade(label='NTP对时', font=font.Font(size=12), menu=self.ntp_time)
        self.menu.add_cascade(label='账号登录', font=font.Font(size=12),
                              command=lambda: self.window.switch_frame(Account_login))
        # 给关于菜单添加菜单栏
        # 选择网站(电商)
        self.url_shop.add_command(label='淘宝', font=font.Font(size=10),
                                  command=lambda: self.url('https://login.taobao.com/'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='京东', font=font.Font(size=10),
                                  command=lambda: self.url('https://passport.jd.com/new/login.aspx'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='苏宁', font=font.Font(size=10),
                                  command=lambda: self.url('https://passport.suning.com/ids/login'))
        # 选择网站(手机)
        self.url_phone.add_command(label='vivo', font=font.Font(size=10),
                                   command=lambda: self.url('https://passport.vivo.com.cn/#/login'))
        self.url_phone.add_separator()  # 分割线
        self.url_phone.add_command(label='oppo', font=font.Font(size=10),
                                   command=lambda: self.url('https://id.oppo.com/index.html'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='小米', font=font.Font(size=10),
                                   command=lambda: self.url('https://account.xiaomi.com/fe/service/login/password'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='华为', font=font.Font(size=10),
                                   command=lambda: self.url('https://id1.cloud.huawei.com/CAS/portal/loginAuth.html'))
        # 购物车选择
        self.buy_car.add_command(label='自动全选(默认)', font=font.Font(size=10),
                                 command=lambda: self.primary('check_all'))
        self.buy_car.add_separator()  # 分割线
        self.buy_car.add_command(label='手动单选', font=font.Font(size=10), command=lambda: self.primary('manual'))
        # 浏览器选择栏
        self.choice_browser.add_command(label='Edge浏览器(默认)', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('edge'))
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='谷歌浏览器', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('chrome'))
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='火狐浏览器', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('firefox'))
        # 手动NTP对时
        self.ntp_time.add_command(label='授时中心(默认)', font=font.Font(size=10), command=self.ntp_timing_china)
        self.ntp_time.add_separator()  # 分割线
        self.ntp_time.add_command(label='阿里云(推荐)', font=font.Font(size=10), command=self.ntp_timing_aliyun)
        # 将菜单栏放入主窗口
        self.window.config(menu=self.menu)
        # 容器
        self.label_buy_time = Label(self, width=100, height=2, bg='#FC1944', bd=5, relief=RIDGE,
                                    font=font.Font(size=12))
        self.label_buy_time['text'] = '请输入秒杀/抢购时间(格式:2000-01-01 20:00:00)'
        self.label_buy_time.pack()
        self.text_time = tkinter.StringVar(value=self.cause_time())
        self.buy_time_entry = Entry(self, width=100, bd=5, justify=CENTER,
                                    textvariable=self.text_time  # 文本框的值,是一个StringVar()对象,这样与StringVar就能更新
                                    # 跟踪变量的值的变化,以保证值的变更随时可以显示在界面上
                                    )  # 文本输入框
        self.buy_time_entry.pack()  # 把text放在window上面,显示text这个控件
        self.label_payment_password = Label(self, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                            font=font.Font(size=12))
        self.label_payment_password['text'] = '请输入支付密码(仅做自动填充,手动输入请留空)'
        self.label_payment_password.pack()
        # 端口input
        payment_password = self.window.register(self.limit_password)  # 需要将函数包装一下,必要的, 否则会直接调用
        self.payment_password_entry = Entry(self,  # 置入容器
                                            width=100, bd=5,
                                            justify=CENTER,  # 居中对齐显示
                                            show='*',  # 显示加密
                                            textvariable=StringVar(),  # 文本框的值,是一个StringVar()对象,这样与StringVar 就能更新
                                            # 跟踪变量的值的变化,以保证值的变更随时可以显示在界面上
                                            validate="key",
                                            # 发生任何变动的时候,就会调用validate-command 这个调动受后面'Key'影响,类似键盘监听 如果换成"focusout"就是光标
                                            validatecommand=(payment_password, '%P'))
        # %P代表输入框的实时内容 # %P表示当输入框的值允许改变,该值有效。
        # 该值为当前文本框内容 # %v(小写大写不一样的),当前validate的值  # %W表示该组件的名字)  # 文本输入框
        self.payment_password_entry.pack()  # 把text放在window上面,显示text这个控件
        # 确定按钮
        self.button = Button(self, height=2, width=20, text="确定", bg='#FC5531', bd=8,
                             command=self.get_parameters)
        self.button.pack()  # 显示按钮

    # 获取参数
    def get_parameters(self):
        acquisition_time_format = compile(
            '^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))\s(([1-9])|([0-1][0-9])|([1-2][0-3])):([0-5][0-9]):([0-5][0-9])$')
        buy_time = self.buy_time_entry.get()
        payment_password = self.payment_password_entry.get()
        if self.url_path is None:
            messagebox.showinfo(title='提示', message='请选择网站')
            return
        elif self.product_selection is None:
            messagebox.showinfo(title='提示', message='请选择是否全选购物车')
            return
        elif not buy_time:
            messagebox.showinfo(title='提示', message='请输入秒杀时间')
            return
        elif acquisition_time_format.match(buy_time) is None:
            messagebox.showwarning(title='警告', message='格式错误\n请检查并输入正确的抢购时间')
            return
        buy_time = acquisition_time.strptime(buy_time, '%Y-%m-%d %H:%M:%S')
        SpikeSystem(self.url_path, self.product_selection, buy_time, payment_password, self.browser,
                    self.login_selection).start()  # 服务器对时


class Account_login(Frame, SpikeSystem_window):
    def __init__(self, window):
        Frame.__init__(self, window)
        self.browser = 'edge'  # 浏览器选择
        self.login_selection = 'account'  # 登录选择
        self.product_selection = 'check_all'  # 购物车选择
        self.url_path = None  # 网址
        self.buy_time = None  # 秒杀时间
        self.account_password = None  # 支付密码
        self.window = window  # 建立窗口window
        self.window.title('秒杀系统4.1(作者:Kearns201)')  # 窗口名称
        width = 620
        height = 430
        # 获取屏幕大小并计算起始坐标
        screen_width = (self.window.winfo_screenwidth() - width) / 2
        screen_height = (self.window.winfo_screenheight() - height) / 2
        # 设置窗口大小以及位置
        self.window.geometry(f'{width}x{height}+{int(screen_width)}+{int(screen_height)}')
        # 控制窗口大小不可更改
        self.window.resizable(False, False)
        # 创建菜单栏
        self.menu = Menu()
        # # 创建菜单
        self.url_shop = Menu(self.menu, tearoff=0)  # 第二个参数是指去掉菜单和菜单栏之间的横线
        self.url_phone = Menu(self.menu, tearoff=0)
        self.buy_car = Menu(self.menu, tearoff=0)
        self.choice_browser = Menu(self.menu, tearoff=0)
        self.ntp_time = Menu(self.menu, tearoff=0)
        # # 将菜单添加到菜单栏中,并添加标签
        self.menu.add_cascade(label='选择网站(电商)', font=font.Font(size=12), menu=self.url_shop)
        self.menu.add_cascade(label='选择网站(手机)', font=font.Font(size=12), menu=self.url_phone)
        self.menu.add_cascade(label='是否全选购物车', font=font.Font(size=12), menu=self.buy_car)
        self.menu.add_cascade(label='选择浏览器', font=font.Font(size=12), menu=self.choice_browser)
        self.menu.add_cascade(label='NTP对时', font=font.Font(size=12), menu=self.ntp_time)
        self.menu.add_cascade(label='扫码登录', font=font.Font(size=12),
                              command=lambda: self.window.switch_frame(QR_code))
        # 给关于菜单添加菜单栏
        # 选择网站(电商)
        self.url_shop.add_command(label='淘宝', font=font.Font(size=10),
                                  command=lambda: self.url('https://login.taobao.com/'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='京东', font=font.Font(size=10),
                                  command=lambda: self.url('https://passport.jd.com/new/login.aspx'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='苏宁', font=font.Font(size=10),
                                  command=lambda: self.url('https://passport.suning.com/ids/login'))
        # 选择网站(手机)
        self.url_phone.add_command(label='vivo', font=font.Font(size=10),
                                   command=lambda: self.url('https://passport.vivo.com.cn/#/login'))
        self.url_phone.add_separator()  # 分割线
        self.url_phone.add_command(label='oppo', font=font.Font(size=10),
                                   command=lambda: self.url('https://id.oppo.com/index.html'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='小米', font=font.Font(size=10),
                                   command=lambda: self.url('https://account.xiaomi.com/fe/service/login/password'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='华为', font=font.Font(size=10),
                                   command=lambda: self.url('https://id1.cloud.huawei.com/CAS/portal/loginAuth.html'))
        # 购物车选择
        self.buy_car.add_command(label='自动全选(默认)', font=font.Font(size=10),
                                 command=lambda: self.primary('check_all'))
        self.buy_car.add_separator()  # 分割线
        self.buy_car.add_command(label='手动单选', font=font.Font(size=10), command=lambda: self.primary('manual'))
        # 浏览器选择栏
        self.choice_browser.add_command(label='Edge浏览器(默认)', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('edge'))
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='谷歌浏览器', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('chrome'))
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='火狐浏览器', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('firefox'))
        # 手动NTP对时
        self.ntp_time.add_command(label='授时中心(默认)', font=font.Font(size=10), command=self.ntp_timing_china)
        self.ntp_time.add_separator()  # 分割线
        self.ntp_time.add_command(label='阿里云(推荐)', font=font.Font(size=10), command=self.ntp_timing_aliyun)
        # 将菜单栏放入主窗口
        self.window.config(menu=self.menu)
        # 容器
        self.label_buy_time = Label(self, width=100, height=2, bg='#FC1944', bd=5, relief=RIDGE,
                                    font=font.Font(size=12))
        self.label_buy_time['text'] = '请输入秒杀/抢购时间(格式:2000-01-01 20:00:00)'
        self.label_buy_time.pack()
        self.text_time = tkinter.StringVar(value=self.cause_time())
        self.buy_time_entry = Entry(self, width=100, bd=5, justify=CENTER,
                                    textvariable=self.text_time  # 文本框的值,是一个StringVar()对象,这样与StringVar就能更新
                                    # 跟踪变量的值的变化,以保证值的变更随时可以显示在界面上
                                    )  # 文本输入框
        self.buy_time_entry.pack()  # 把text放在window上面,显示text这个控件
        self.label_payment_password = Label(self, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                            font=font.Font(size=12))
        self.label_payment_password['text'] = '请输入支付密码(仅做自动填充,手动输入请留空)'
        self.label_payment_password.pack()
        # 端口input
        payment_password = self.window.register(self.limit_password)  # 需要将函数包装一下,必要的, 否则会直接调用
        self.payment_password_entry = Entry(self,  # 置入容器
                                            width=100, bd=5,
                                            justify=CENTER,  # 居中对齐显示
                                            show='*',  # 显示加密
                                            textvariable=StringVar(),  # 文本框的值,是一个StringVar()对象,这样与StringVar 就能更新
                                            # 跟踪变量的值的变化,以保证值的变更随时可以显示在界面上
                                            validate="key",
                                            # 发生任何变动的时候,就会调用validate-command 这个调动受后面'Key'影响,类似键盘监听 如果换成"focusout"就是光标
                                            validatecommand=(
                                                payment_password, '%P'))  # %P代表输入框的实时内容 # %P表示 当输入框的值允许改变,该值有效。
        # 该值为当前文本框内容 # %v(小写大写不一样的),当前validate的值  # %W表示该组件的名字)  # 文本输入框
        self.payment_password_entry.pack()  # 把text放在window上面,显示text这个控件
        self.label_account = Label(self, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                   font=font.Font(size=12))
        self.label_account['text'] = '请输入账号(仅做自动填充,手动输入请留空)'
        self.label_account.pack()
        self.account_entry = Entry(self, width=100, bd=5, justify=CENTER)  # 文本输入框
        self.account_entry.pack()  # 把text放在window上面,显示text这个控件
        self.label_account_password = Label(self, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                            font=font.Font(size=12))
        self.label_account_password['text'] = '请输入密码(仅做自动填充,手动输入请留空)'
        self.label_account_password.pack()
        self.account_password_entry = Entry(self, width=100, bd=5, justify=CENTER, show='*')  # 文本输入框
        self.account_password_entry.pack()  # 把text放在window上面,显示text这个控件
        # 确定按钮
        self.button = Button(self, height=2, width=20, text="确定", bg='#FC5531', bd=8,
                             command=self.get_parameters)
        self.button.pack()  # 显示按钮

    # 获取参数
    def get_parameters(self):
        acquisition_time_format = compile(
            '^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))\s(([1-9])|([0-1][0-9])|([1-2][0-3])):([0-5][0-9]):([0-5][0-9])$')
        buy_time = self.buy_time_entry.get()
        payment_password = self.payment_password_entry.get()
        account = self.account_entry.get()
        account_password = self.account_password_entry.get()
        if self.url_path is None:
            messagebox.showinfo(title='提示', message='请选择网站')
            return
        elif self.product_selection is None:
            messagebox.showinfo(title='提示', message='请选择是否全选购物车')
            return
        elif not buy_time:
            messagebox.showinfo(title='提示', message='请输入秒杀时间')
            return
        elif acquisition_time_format.match(buy_time) is None:
            messagebox.showwarning(title='警告', message='格式错误\n请检查并输入正确的抢购时间')
            return
        buy_time = acquisition_time.strptime(buy_time, '%Y-%m-%d %H:%M:%S')
        SpikeSystem(self.url_path, self.product_selection, buy_time, payment_password, self.browser,
                    self.login_selection, account, account_password).start()  # 服务器对时


class SpikeSystem:
    def __init__(self, url_path, product_selection, buy_time, password, browser, login_selection, account=None,
                 account_password=None):
        self.thread = None  # 多线程
        self.driver = None  # 浏览器驱动
        self.options = None  # 浏览器爬虫伪装参数
        self.browser = browser  # 浏览器选择
        self.login_selection = login_selection  # 登录选择
        self.account = account  # 账户名
        self.account_password = account_password  # 账户密码
        self.url_path = url_path  # 网站链接
        self.product_selection = product_selection  # 选择的商品
        self.buy_time = buy_time  # 购买时间
        self.password = password  # 支付密码
        self.time_remaining = datetime.timedelta(seconds=4)  # 剩余时间

    # 多线程
    def start(self):
        # 判断是否有线程在运行
        if self.thread is not None:
            messagebox.showinfo('提示', '参数已更新\n点击确定重新调用程序')
            try:
                self.driver.quit()
                self.thread = None
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
                    self.oppo()  # oppo
                if self.url_path == 'https://account.xiaomi.com/fe/service/login/password':
                    self.xiaomi()  # 小米
                if self.url_path == 'https://id1.cloud.huawei.com/CAS/portal/loginAuth.html':
                    self.huawei()  # 华为
        except InvalidSessionIdException:
            return False
        except WebDriverException:  # 驱动未调用成功
            return False
        except Exception:
            return False

    # 浏览器驱动函数
    def drivers(self):
        self.driver = self.online_driver()
        self.driver.implicitly_wait(8)  # 隐式等待
        return self.driver  # 返回浏览器驱动程序

    # 调用在线驱动
    def online_driver(self):
        online_driver = None
        browser_service = {'edge': edgeService, 'chrome': chromeService, 'firefox': firefoxService}  # 新特性service容器
        browser = {'edge': webdriver.Edge, 'chrome': webdriver.Chrome, 'firefox': webdriver.Firefox}  # 选择浏览器
        try:
            if self.browser == 'edge':
                online_driver = EdgeChromiumDriverManager().install()
                self.options = edgeOptions()
            elif self.browser == 'chrome':
                online_driver = ChromeDriverManager().install()
                self.options = chromeOptions()
            elif self.browser == 'firefox':
                online_driver = GeckoDriverManager().install()
                self.options = firefoxOptions()
            self.options.add_argument("--disable-blink-features")
            self.options.add_argument("--disable-blink-features=AutomationControlled")
            service = browser_service[self.browser](online_driver)  # service容器
            self.driver = browser[self.browser](service=service, options=self.options)  # 启动浏览器驱动
        except WebDriverException:
            messagebox.showerror(title='错误:启动失败', message='请确认是否安装了相应的浏览器')
        except requests.exceptions.SSLError:
            messagebox.showwarning('警告', '请检测并关闭VPN应用')
        except requests.exceptions.ConnectionError:
            messagebox.showerror('错误', '请确认网络连接是否正常')
        return self.driver

    # 扫码登录函数
    def qr_login(self, url, detection, qr_login=None, detection_choice=True):
        """
        :param url: 要跳转的购物车链接地址
        :param detection: 用以检测是否离开当前页面
        :param qr_login: 默认为空,表示不需要点击扫码登录,否则传入扫码登录的元素
        :param detection_choice: 默认为真，表示detection在当前页面，假表示在下一页面
        :return: 布尔值
        """
        self.driver.get(self.url_path)
        if qr_login is None:
            pass
        else:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, qr_login))).click()
        if detection_choice:
            while True:
                try:
                    self.driver.find_element(By.XPATH, detection).is_displayed()
                    sleep(1)
                except NoSuchElementException:
                    self.driver.get(url)
                    break
            # WebDriverWait(self.driver, 100).until_not(ec.visibility_of_element_located((By.XPATH, detection)))
        else:
            WebDriverWait(self.driver, 100).until(ec.presence_of_element_located((By.XPATH, detection)))
            self.driver.get(url)

    # 账号登录函数
    def account_login(self, url, detection, account=None, account_password=None, login_chick=None, account_login=None,
                      detection_choice=True):
        """
        :param url: 要跳转的购物车链接地址
        :param detection: 用以检测是否离开当前页面
        :param account: 账号输入框
        :param account_password: 密码输入框
        :param login_chick: 登录按钮
        :param account_login: 默认为空,表示不需要点击账号登录,否则传入账号登录的元素
        :param detection_choice: 默认为真，表示detection在当前页面，假表示在下一页面
        :return: 布尔值
        """
        self.driver.get(self.url_path)
        if account is None:
            pass
        else:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, account_login))).click()
            if account_login is None:
                pass
            else:
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, account))).send_keys(
                    self.account)
                WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, account_password))).send_keys(
                    self.account_password)
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, login_chick))).click()
        if detection_choice:
            WebDriverWait(self.driver, 100).until_not(ec.visibility_of_element_located((By.XPATH, detection)))
            self.driver.get(url)
        else:
            WebDriverWait(self.driver, 100).until(ec.presence_of_element_located((By.XPATH, detection)))
            self.driver.get(url)

    # 全选函数
    def check(self, check_box, check_login=None, agree=None):
        """
        :param check_box: 传入全选框的Xpath
        :param check_login: 默认值为空, 传入购物车页面需要二次点击登录的元素
        :param agree: 默认值为空, 传入购物车页面需要点击同意的元素
        :return: 布尔值
        """
        if check_login is None:
            pass
        else:
            # 二次点击登录
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, check_login))).click()
            # 同意协议
            if agree is None:
                pass
            else:
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, agree))).click()
        if self.product_selection == 'check_all':
            # 全选购物车
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, check_box)))  # 等待全选框加载完毕
            if self.driver.find_element(By.XPATH, check_box).is_selected():
                pass
            else:
                self.driver.find_element(By.XPATH, check_box).click()
        else:
            pass

    # 秒杀函数
    def seckill(self, settlement, submit, address=None):
        """
        :param settlement: 传入购物车页面的结算按钮Xpath
        :param submit: 传入地址确认页面的提交按钮Xpath
        :param address: 默认值为空, 传入地址确认页面的地址选择Xpath
        :return: 布尔值
        """
        # 循环对比时间
        while True:
            # 获取当前时间
            now_time = acquisition_time.now()
            # 判断当前时间是否大于设定时间
            if now_time >= self.buy_time:
                # 如果大于设定时间,则点击购买按钮
                self.driver.find_element(By.XPATH, settlement).click()
                # 选择地址
                if address is None:
                    pass
                else:
                    WebDriverWait(self.driver, 5, 0.001).until(
                        ec.presence_of_element_located((By.XPATH, address))).click()
                # 点击提交按钮
                WebDriverWait(self.driver, 5, 0.001).until(ec.presence_of_element_located((By.XPATH, submit))).click()
                break
            if (self.buy_time - now_time) > self.time_remaining:
                sleep(3)

    # 付款函数
    def pay(self, input_box=None, enter=None, click_to_pay=None):
        """
        :param input_box: 传入密码输入框Xpath
        :param enter: 默认为空,传入确认付款按钮Xpath
        :param click_to_pay: 默认为空,传入点击去付款调出输入框按钮Xpath
        :return: 布尔值
        """
        if click_to_pay is None:
            pass
        else:
            # 点击支付按钮
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, click_to_pay))).click()
            if input_box is None:
                pass
            else:
                if self.password is not None and self.password.isspace() is False and self.password.isnumeric() and len(
                        self.password) == 6:
                    # 判断是否有输入框
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, input_box)))
                    for i in range(len(self.password)):
                        pyautogui.press(self.password[i])
                    if enter is None:
                        pyautogui.press('enter')
                    else:
                        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, enter))).click()
                    sleep(10)
                    self.driver.quit()  # 退出浏览器函数
                else:
                    pass

    # 淘宝函数
    def taobao(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://cart.taobao.com/cart.htm', '//*[@id="header"]/div/div/a[2]',
                          '//*[@id="login"]/div[1]/i')
        else:
            self.account_login('https://cart.taobao.com/cart.htm', '//*[@id="header"]/div/div/a[2]',
                               '//*[@id="fm-login-id"]', '//*[@id="fm-login-password"]',
                               '//*[@id="login-form"]/div[4]/button')
        self.check('//*[@id="J_SelectAll1"]/div/label')
        self.seckill('//*[@id="J_Go"]', '//*[@id="submitOrderPC_1"]/div[1]/a[2]')
        self.pay('//*[@id="payPassword_container"]/div')

    # 京东函数
    def jd(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://cart.jd.com/cart_index', '/html/body/div[1]/a')
        else:
            self.account_login('https://cart.jd.com/cart_index', '/html/body/div[1]/a',
                               '//*[@id="loginname"]', '//*[@id="nloginpwd"]',
                               '//*[@id="loginsubmit"]', '//*[@id="content"]/div[2]/div[1]/div/div[3]/a')
        self.check('//*[@id="cart-body"]/div[2]/div[3]/div[1]/div/input')
        self.seckill('//*[@id="cart-body"]/div[2]/div[16]/div/div[2]/div/div/div/div[2]/div[2]/div/div[1]/a/b',
                     '//*[@id="order-submit"]')
        self.pay('//*[@id="validateShortFake"]', '//*[@id="baseMode"]/div/div[2]/div/div[2]/div/div/div[1]',
                 '//*[@id="indexBlurId"]/div/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/div/div[1]')

    # 苏宁函数
    def suning(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://shopping.suning.com/cart.do#resize:380,450', '//*[@id="LOGIN_ADVISE"]')
        else:
            self.account_login('https://shopping.suning.com/cart.do#resize:380,450', '//*[@id="LOGIN_ADVISE"]',
                               '//*[@id="userName"]', '//*[@id="password"]',
                               '//*[@id="submit"]', '/html/body/div[2]/div[1]/div/div[1]/a[2]')
        self.check('//*[@id="chooseAllCheckFrame2"]')
        self.seckill('//*[@id="cart-wrapper"]/div[3]/div/div/div[2]/div[2]/a', '//*[@id="submit-btn"]')

    # vivo函数
    def vivo(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://shop.vivo.com.cn/shoppingcart', '/html/body/div[1]/div[3]/div[1]/div/div[1]/a',
                          '/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/img[2]')
        else:
            self.account_login('https://shop.vivo.com.cn/shoppingcart', '/html/body/div[1]/div[3]/div[1]/div/div[1]/a',
                               '/html/body/div[1]/div[3]/div[1]/div/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/input',
                               '/html/body/div[1]/div[3]/div[1]/div/div[2]/div[3]/div[2]/div[2]/div[1]/div[3]/input',
                               '/html/body/div[1]/div[3]/div[1]/div/div[2]/div[3]/div[6]',
                               '/html/body/div[1]/div[3]/div[1]/div/div[2]/div[3]/div[1]/span[2]')
        self.check('//*[@id="fixed-bottom-bar"]/div/div/div[1]/ul/li[1]/label/a')
        self.seckill('//*[@id="fixed-bottom-bar"]/div/div/div[2]/table/tr/td[2]/button', 'btn-submit')

    # oppo函数
    def oppo(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://www.opposhop.cn/cn/web/cart', '//*[@id="root"]/div/div[1]/div/div[2]/div[3]',
                          '//*[@id="root"]/div/div[3]/div/div[2]/div/div[1]/div[2]', False)
        else:
            self.account_login('https://www.opposhop.cn/cn/web/cart', '//*[@id="root"]/div/div[1]/div/div[2]/div[3]',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div['
                               '1]/div/div/div/div[2]/input',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div['
                               '2]/div/div/div[1]/input',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div[4]',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/span')
        self.check('//*[@id="input-36"]')
        self.seckill('//*[@id="app"]/div/div[1]/main/div/div[2]/div/div[1]/div[3]/button',
                     '//*[@id="app"]/div/div[1]/div/main/div/div[8]/div/div/div[3]/button')

    # 小米函数
    def xiaomi(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://www.mi.com/shop/buy/cart', '//*[@id="root"]/div/div/div[1]/div[2]/span/span',
                          '//*[@id="root"]/div/div/div[2]/div/div/div[2]/div/div[1]/div[1]', False)
        else:
            self.account_login('https://www.mi.com/shop/buy/cart', '//*[@id="root"]/div/div/div[1]/div[2]/span/span',
                               '//*[@id="rc-tabs-0-panel-login"]/form/div[1]/div[1]/div[2]/div/div/div/div/input',
                               '//*[@id="rc-tabs-0-panel-login"]/form/div[1]/div[2]/div/div[1]/div/input',
                               '//*[@id="rc-tabs-0-panel-login"]/form/div[1]/button',
                               '//*[@id="rc-tabs-0-panel-login"]/form/div[1]/div[3]/label/span[1]/input')
        self.check('//*[@id="app"]/div[2]/div/div/div/div[1]/div[2]/div[1]/div[1]/i',
                   '/html/body/div/div[2]/div/div/div/div/div[1]/a[1]',
                   '//*[@id="stat_e3c9df7196008778"]/div[2]/div[2]/div/div/div/div[3]/button[1]')
        self.seckill('//*[@id="app"]/div[2]/div/div/div/div[1]/div[4]/span/a',
                     '//*[@id="app"]/div[2]/div/div/div[2]/div/div[6]/div[2]/div/a[1]'
                     , '//*[@id="app"]/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]')
        self.pay(click_to_pay='//*[@id="app"]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/ul/li[1]/img')

    # 华为函数
    def huawei(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://www.vmall.com/cart', '/html/body/div/div/div[1]/div[3]/div[2]/span/span')
        else:
            self.account_login('https://www.vmall.com/cart', '/html/body/div/div/div[1]/div[3]/div[2]/span/span',
                               '/html/body/div[1]/div/div[1]/div[3]/div[3]/span[3]/div[1]/form/div[2]/div/div/div/input',
                               '/html/body/div[1]/div/div[1]/div[3]/div[3]/span[3]/div[1]/form/div[3]/div/div/div/input',
                               '/html/body/div[1]/div/div[1]/div[3]/div[3]/span[3]/div[1]/div[2]/div/div/div')
        self.check('//*[@id="app"]/div[2]/div[3]/div[4]/div/div[1]/label/input',
                   '//*[@id="app"]/div[2]/div[3]/div[1]/a', '//*[@id="ecBoxID"]/div[2]/div[3]/a[2]')
        self.seckill('//*[@id="app"]/div[2]/div[3]/div[4]/div/div[2]/a', '//*[@id="checkoutSubmit"]')
        self.pay(click_to_pay='/html/body/div[1]/div/div/ul/li/button')


if __name__ == '__main__':
    # 实例化对象
    # messagebox.showinfo('使用说明', '请依次选择网站, 购物车, 浏览器, NTP一般不用选择, 在每次选择网站的适合都会自动对时, 正因如此, 有时候程序会响应3-5秒左右, '
    #                                 '因为国家授时中心对时协议特殊导致的, 密码无需担心泄露, 软件密文加密, 输入仅用于无人值守时全自动化抢购, '
    #                                 '如若不放心可以稍后抢购成功后手动输入')
    Spike = SpikeSystem_window()
    Spike.mainloop()  # 显示窗口
