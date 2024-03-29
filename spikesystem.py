# pyinstaller spikesystem.py -F -w -i favicon.ico
import os
import socket
import time
import tkinter
from _datetime import datetime as acquisition_time  # 不同模块取别名
from datetime import datetime
from datetime import timedelta
from re import compile
from threading import Thread
from time import sleep
from tkinter import *
from tkinter import font
from tkinter import messagebox

import ntplib
import requests.exceptions
from pyautogui import press
from pyautogui import typewrite
from selenium import webdriver  # 导入webdriver模块
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
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

    def on_ret(self, ev):
        if self.widgetName == "button":
            self.invoke()  # 回车确认
        elif self.widgetName == "entry":
            self.event_generate('<<NextWindow>>')  # 回车后跳转下一个窗口
        return "break"

    # 网址选择
    def url(self, url):
        url_dictionary = {'淘宝': 'https://login.taobao.com/', '京东': 'https://passport.jd.com/new/login.aspx',
                          '苏宁': 'https://passport.suning.com/ids/login',
                          'vivo': 'https://passport.vivo.com.cn/#/login', 'oppo': 'https://id.oppo.com/index.html',
                          '小米': 'https://account.xiaomi.com/fe/service/login/password',
                          '华为': 'https://account.xiaomi.com/fe/service/login/password'}  # 网址字典
        self.url_path = url_dictionary[url]
        messagebox.showinfo('网址选择成功', '当前网址为 :   ' + url + '\n自动对时中 . . . ')
        messagebox.showinfo('对时成功', '对时结果为 :   ' + self.ntp_timing_aliyun('auto'))

    # 购物车选择
    def primary(self, choice):
        choice_dictionary = {'自动全选': 1, '手动单选': 0}  # 购物车字典
        self.shoppingcart_selection = choice_dictionary[choice]
        messagebox.showinfo('购物车倾向选择成功', '当前购物车倾向为 :   ' + choice)

    # 浏览器选择
    def browser_choice(self, browser):
        self.browser = browser
        messagebox.showinfo('浏览器选择成功', '当前浏览器为 :   ' + browser)

    @staticmethod
    def verify_ntp_time(time_server, mode):
        try:
            response = ntplib.NTPClient().request(time_server)
            ts = response.tx_time
            _date = time.strftime('%Y-%m-%d', time.localtime(ts))
            _time = time.strftime('%X', time.localtime(ts))
            os.system('date {} && time {}'.format(_date, _time))
            ntp = time.strftime('%Y-%m-%d %X', time.localtime(ts))
            local = datetime.now().strftime('%Y-%m-%d %X')
            if ntp == local:
                if mode == 'manual':
                    messagebox.showinfo('对时成功', '对时结果为 :   ' + local)
                    return True
                else:
                    if mode == 'auto':
                        return local
        except socket.gaierror:
            messagebox.showerror('对时失败', '请检查网络连接后再手动对时')
            return False
        except ntplib.NTPException:
            messagebox.showwarning('对时失败', '时间服务器无响应\n请手动NTP对时或选择其他NTP服务器')
            return False

    # 对时国家授时中心
    def ntp_timing_china(self, mode='manual'):
        return self.verify_ntp_time('ntp.ntsc.ac.cn', mode)

    # 对时阿里云NTP服务器
    def ntp_timing_aliyun(self, mode='manual'):
        return self.verify_ntp_time('ntp.aliyun.com', mode)

    # 时间自动优化
    @staticmethod
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

    # 密码限制
    @staticmethod
    def limit_password(data):
        # 如果不加上==""的话,就会发现删不完。总会剩下一个数字 isdigit函数：isdigit函数方法检测字符串是否只由数字组成。
        if (data.isdigit() and len(data) <= 6) or data == "":
            return True
        else:
            return False


class MyEntry(Entry, SpikeSystem_window):
    def __init__(self, master, **kw):
        Entry.__init__(self, master, **kw)
        self.next_widget = None
        self.bind("<Return>", self.on_ret)


class MyButton(Button, SpikeSystem_window):
    def __init__(self, master, **kw):
        Button.__init__(self, master, **kw)
        self.next_widget = None
        self.bind("<Return>", self.on_ret)


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
        MyButton(self, text="扫码登录", height=2, width=20, bg='#FC5531', bd=8,
                 command=lambda: self.window.switch_frame(QR_code)).pack()
        MyButton(self, text="账号登录", height=2, width=20, bg='#FC5531', bd=8,
                 command=lambda: self.window.switch_frame(Account_login)).pack()


class QR_code(Frame, SpikeSystem_window):
    # 启动程序
    def __init__(self, window):
        Frame.__init__(self, window)
        self.browser = 'edge'  # 浏览器选择
        self.login_selection = 'qr_code'  # 登录方式选择
        self.url_path = None  # 网址
        self.buy_time = None  # 秒杀时间
        self.password = None  # 支付密码
        self.shoppingcart_selection = 'manual'  # 购物车选择
        self.window = window  # 建立窗口window
        self.window.title('秒杀系统6.0(作者:Kearns201)')  # 窗口名称
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
        self.menu.add_cascade(label='选择网站(电商)*', font=font.Font(size=12), menu=self.url_shop)
        self.menu.add_cascade(label='选择网站(手机)*', font=font.Font(size=12), menu=self.url_phone)
        self.menu.add_cascade(label='购物车选择', font=font.Font(size=12), menu=self.buy_car)
        self.menu.add_cascade(label='浏览器选择', font=font.Font(size=12), menu=self.choice_browser)
        self.menu.add_cascade(label='NTP对时', font=font.Font(size=12), menu=self.ntp_time)
        self.menu.add_cascade(label='账号登录', font=font.Font(size=12),
                              command=lambda: self.window.switch_frame(Account_login))
        # 给关于菜单添加菜单栏
        # 选择网站(电商)
        self.url_shop.add_command(label='淘宝', font=font.Font(size=10),
                                  command=lambda: self.url('淘宝'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='京东', font=font.Font(size=10),
                                  command=lambda: self.url('京东'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='苏宁', font=font.Font(size=10),
                                  command=lambda: self.url('苏宁'))
        # 选择网站(手机)
        self.url_phone.add_command(label='vivo', font=font.Font(size=10),
                                   command=lambda: self.url('vivo'))
        self.url_phone.add_separator()  # 分割线
        self.url_phone.add_command(label='oppo', font=font.Font(size=10),
                                   command=lambda: self.url('oppo'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='小米', font=font.Font(size=10),
                                   command=lambda: self.url('小米'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='华为', font=font.Font(size=10),
                                   command=lambda: self.url('华为'))
        # 购物车选择
        self.buy_car.add_command(label='自动全选', font=font.Font(size=10),
                                 command=lambda: self.primary('自动全选'))
        self.buy_car.add_separator()  # 分割线
        self.buy_car.add_command(label='手动单选(默认)', font=font.Font(size=10),
                                 command=lambda: self.primary('手动单选'))
        # 浏览器选择栏
        self.choice_browser.add_command(label='谷歌浏览器', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('chrome'))
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='Edge浏览器(默认)', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('edge'))
        # 手动NTP对时
        self.ntp_time.add_command(label='国家授时中心', font=font.Font(size=10), command=self.ntp_timing_china)
        self.ntp_time.add_separator()  # 分割线
        self.ntp_time.add_command(label='阿里云(默认)', font=font.Font(size=10), command=self.ntp_timing_aliyun)
        # 将菜单栏放入主窗口
        self.window.config(menu=self.menu)
        # 容器
        self.label_buy_time = Label(self, width=100, height=2, bg='#FC1944', bd=5, relief=RIDGE,
                                    font=font.Font(size=12))
        self.label_buy_time['text'] = '请输入秒杀/抢购时间(格式:2000-01-01 20:00:00)'
        self.label_buy_time.pack()
        self.text_time = tkinter.StringVar(value=self.cause_time())
        self.buy_time_entry = MyEntry(self, width=100, bd=5, justify=CENTER,
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
        self.payment_password_entry = MyEntry(self,  # 置入容器
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
        self.button = MyButton(self, height=2, width=20, text="确定", bg='#FC5531', bd=8,
                               command=self.get_parameters)
        self.button.pack()  # 显示按钮

    # 获取参数
    def get_parameters(self):
        self.button['state'] = 'disabled'  # 禁用按钮
        acquisition_time_format = compile(
            '^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))\s(([1-9])|([0-1][0-9])|([1-2][0-3])):([0-5][0-9]):([0-5][0-9])$')
        buy_time = self.buy_time_entry.get()
        payment_password = self.payment_password_entry.get()
        if self.url_path is None:
            messagebox.showinfo(title='提示', message='请选择网站')
            return
        elif acquisition_time_format.match(buy_time) is None:
            messagebox.showwarning(title='格式错误', message='请检查并输入正确的抢购时间')
            return
        buy_time = acquisition_time.strptime(buy_time, '%Y-%m-%d %H:%M:%S')
        SpikeSystem(self.url_path, self.shoppingcart_selection, buy_time, payment_password, self.browser,
                    self.login_selection).start()  # 服务器对时


class Account_login(Frame, SpikeSystem_window):
    def __init__(self, window):
        Frame.__init__(self, window)
        self.browser = 'edge'  # 浏览器选择
        self.login_selection = 'account'  # 登录选择
        self.url_path = None  # 网址
        self.buy_time = None  # 秒杀时间
        self.account_password = None  # 支付密码
        self.shoppingcart_selection = 'manual'  # 购物车选择
        self.window = window  # 建立窗口window
        self.window.title('秒杀系统6.0(作者:Kearns201)')  # 窗口名称
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
        self.menu.add_cascade(label='选择网站(电商)*', font=font.Font(size=12), menu=self.url_shop)
        self.menu.add_cascade(label='选择网站(手机)*', font=font.Font(size=12), menu=self.url_phone)
        self.menu.add_cascade(label='购物车选择', font=font.Font(size=12), menu=self.buy_car)
        self.menu.add_cascade(label='浏览器选择', font=font.Font(size=12), menu=self.choice_browser)
        self.menu.add_cascade(label='NTP对时', font=font.Font(size=12), menu=self.ntp_time)
        self.menu.add_cascade(label='扫码登录', font=font.Font(size=12),
                              command=lambda: self.window.switch_frame(QR_code))
        # 给关于菜单添加菜单栏
        # 选择网站(电商)
        self.url_shop.add_command(label='淘宝', font=font.Font(size=10),
                                  command=lambda: self.url('淘宝'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='京东', font=font.Font(size=10),
                                  command=lambda: self.url('京东'))
        self.url_shop.add_separator()  # 分割线
        self.url_shop.add_command(label='苏宁', font=font.Font(size=10),
                                  command=lambda: self.url('苏宁'))
        # 选择网站(手机)
        self.url_phone.add_command(label='vivo', font=font.Font(size=10),
                                   command=lambda: self.url('vivo'))
        self.url_phone.add_separator()  # 分割线
        self.url_phone.add_command(label='oppo', font=font.Font(size=10),
                                   command=lambda: self.url('oppo'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='小米', font=font.Font(size=10),
                                   command=lambda: self.url('小米'))
        self.url_phone.add_separator()
        self.url_phone.add_command(label='华为', font=font.Font(size=10),
                                   command=lambda: self.url('华为'))
        # 购物车选择
        self.buy_car.add_command(label='自动全选', font=font.Font(size=10),
                                 command=lambda: self.primary('自动全选'))
        self.buy_car.add_separator()  # 分割线
        self.buy_car.add_command(label='手动单选(默认)', font=font.Font(size=10),
                                 command=lambda: self.primary('手动单选'))
        # 浏览器选择栏
        self.choice_browser.add_command(label='谷歌浏览器', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('chrome'))
        self.choice_browser.add_separator()  # 分割线
        self.choice_browser.add_command(label='Edge浏览器(默认)', font=font.Font(size=10),
                                        command=lambda: self.browser_choice('edge'))
        # 手动NTP对时
        self.ntp_time.add_command(label='国家授时中心', font=font.Font(size=10), command=self.ntp_timing_china)
        self.ntp_time.add_separator()  # 分割线
        self.ntp_time.add_command(label='阿里云(默认)', font=font.Font(size=10), command=self.ntp_timing_aliyun)
        # 将菜单栏放入主窗口
        self.window.config(menu=self.menu)
        # 容器
        self.label_buy_time = Label(self, width=100, height=2, bg='#FC1944', bd=5, relief=RIDGE,
                                    font=font.Font(size=12))
        self.label_buy_time['text'] = '请输入秒杀/抢购时间(格式:2000-01-01 20:00:00)'
        self.label_buy_time.pack()
        self.text_time = tkinter.StringVar(value=self.cause_time())
        self.buy_time_entry = MyEntry(self, width=100, bd=5, justify=CENTER,
                                      textvariable=self.text_time  # 文本框的值,是一个StringVar()对象,这样与StringVar就能更新
                                      # 跟踪变量的值的变化,以保证值的变更随时可以显示在界面上
                                      )  # 文本输入框
        self.buy_time_entry.pack()  # 把text放在window上面,显示text这个控件
        self.label_account = Label(self, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                   font=font.Font(size=12))
        self.label_account['text'] = '请输入账号(仅做自动填充,手动输入请留空)'
        self.label_account.pack()
        self.account_entry = MyEntry(self, width=100, bd=5, justify=CENTER)  # 文本输入框
        self.account_entry.pack()  # 把text放在window上面,显示text这个控件
        self.label_account_password = Label(self, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                            font=font.Font(size=12))
        self.label_account_password['text'] = '请输入密码(仅做自动填充,手动输入请留空)'
        self.label_account_password.pack()
        self.account_password_entry = MyEntry(self, width=100, bd=5, justify=CENTER, show='*')  # 文本输入框
        self.account_password_entry.pack()  # 把text放在window上面,显示text这个控件
        self.label_payment_password = Label(self, width=100, height=2, bg='#935167', bd=5, relief=RIDGE,
                                            font=font.Font(size=12))
        self.label_payment_password['text'] = '请输入支付密码(仅做自动填充,手动输入请留空)'
        self.label_payment_password.pack()
        # 端口input
        payment_password = self.window.register(self.limit_password)  # 需要将函数包装一下,必要的, 否则会直接调用
        self.payment_password_entry = MyEntry(self,  # 置入容器
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
        # 确定按钮
        self.button = MyButton(self, height=2, width=20, text="确定", bg='#FC5531', bd=8,
                               command=self.get_parameters)
        self.button.pack()  # 显示按钮

    # 获取参数
    def get_parameters(self):
        self.button['state'] = DISABLED  # 禁用按钮
        acquisition_time_format = compile(
            '^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))\s(([1-9])|([0-1][0-9])|([1-2][0-3])):([0-5][0-9]):([0-5][0-9])$')
        buy_time = self.buy_time_entry.get()
        account = self.account_entry.get()
        if account == '':
            account = None
        account_password = self.account_password_entry.get()
        payment_password = self.payment_password_entry.get()
        if self.url_path is None:
            messagebox.showinfo(title='提示', message='请选择网站')
            return
        elif acquisition_time_format.match(buy_time) is None:
            messagebox.showwarning(title='格式错误', message='请检查并输入正确的抢购时间')
            return
        buy_time = acquisition_time.strptime(buy_time, '%Y-%m-%d %H:%M:%S')
        SpikeSystem(self.url_path, self.shoppingcart_selection, buy_time, payment_password, self.browser,
                    self.login_selection, account, account_password).start()  # 服务器对时


class SpikeSystem:
    def __init__(self, url_path, shoppingcart_selection, buy_time, password, browser, login_selection, account=None,
                 account_password=None):
        self.thread = None  # 线程
        self.driver = None  # 浏览器驱动
        self.options = None  # 浏览器爬虫伪装参数
        self.time_remaining = timedelta(seconds=4)  # 剩余时间
        self.url_path = url_path  # 网站链接
        self.shoppingcart_selection = shoppingcart_selection  # 选择的商品
        self.buy_time = buy_time  # 购买时间
        self.password = password  # 支付密码
        self.browser = browser  # 浏览器选择
        self.login_selection = login_selection  # 登录选择
        self.account = account  # 账户名
        self.account_password = account_password  # 账户密码

    # 多线程
    def start(self):
        self.thread = Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    # 秒杀主程序
    def run(self):
        try:
            self.driver = self.online_driver()  # 调用浏览器驱动
            if self.driver is None:
                return False
            else:
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
                Spike.destroy()
        except InvalidSessionIdException:  # 浏览器被关闭
            return False
        except WebDriverException:  # 驱动未调用成功
            return False
        except Exception:  # 其他异常
            return False

    # 在线驱动
    def online_driver(self):
        driver = None
        browser_service = {'edge': EdgeService, 'chrome': ChromeService}  # 新特性service容器
        browser = {'edge': webdriver.Edge, 'chrome': webdriver.Chrome}  # 选择浏览器
        try:
            if self.browser == 'edge':
                driver = EdgeChromiumDriverManager(path=r".\\Drivers").install()
                self.options = EdgeOptions()
            elif self.browser == 'chrome':
                driver = ChromeDriverManager(path=r".\\Drivers").install()
                self.options = ChromeOptions()

            self.options.add_argument("--disable-blink-features=AutomationControlled")  # 禁止自动化控制
            self.options.add_argument("--disable-blink-features")  # 禁止浏览器检测
            self.options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 隐藏selenium
            self.options.add_experimental_option('useAutomationExtension', False)  # 禁止浏览器检测
            self.options.add_argument('--disable-extensions')  # 禁用扩展
            self.options.add_argument('--start-maximized')  # 最大化窗口

            service = browser_service[self.browser](driver)  # service容器
            self.driver = browser[self.browser](service=service, options=self.options)  # 启动浏览器驱动
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {  # 驱动伪装
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                    })
                """
            })
        except WebDriverException:
            messagebox.showerror(title='错误:启动失败', message='请确认是否安装了相应的浏览器')
        except requests.exceptions.SSLError:
            messagebox.showwarning('警告', '请检测并关闭VPN应用')
        except requests.exceptions.ConnectionError:
            messagebox.showerror('错误', '请确认网络连接是否正常')
        return self.driver

    # 扫码登录函数
    def qr_login(self, url, detection, qr_login=None):
        """
        :param url: 要跳转的购物车链接地址
        :param detection: 用以检测是否离开当前页面
        :param qr_login: 默认为空,表示不需要点击扫码登录,否则传入扫码登录的元素
        """
        self.driver.get(self.url_path)  # 打开登录页面
        if qr_login is None:
            pass
        else:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, qr_login))).click()
        WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH, detection)))  # 等待扫码登录
        self.driver.get(url)

    # 账号登录函数
    def account_login(self, url, detection, account=None, account_password=None, login_chick=None, account_login=None):
        """
        :param url: 要跳转的购物车链接地址
        :param detection: 用以检测是否离开当前页面
        :param account: 账号输入框
        :param account_password: 密码输入框
        :param login_chick: 登录按钮
        :param account_login: 默认为空,表示不需要点击账号登录,否则传入账号登录的元素
        """
        self.driver.get(self.url_path)
        if account_login is None:
            pass
        else:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, account_login))).click()
        if self.account is None:  # 判断是否需要输入账号密码
            pass
        else:
            sleep(3)
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, account))).send_keys(
                self.account)
            WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.XPATH, account_password))).send_keys(
                self.account_password)
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, login_chick))).click()
        WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH, detection)))
        self.driver.get(url)

    # 全选函数
    def check(self, check_box, check_login=None, agree=None):
        """
        :param check_box: 传入全选框的Xpath
        :param check_login: 默认值为空, 传入购物车页面需要二次点击登录的元素
        :param agree: 默认值为空, 传入购物车页面需要点击同意的元素
        """
        if check_login is None:
            pass
        else:
            # 二次点击登录
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, check_login))).click()
            # 同意协议
            if agree is None:
                pass
            else:
                WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, agree))).click()
        if self.shoppingcart_selection == 1:
            # 全选购物车
            WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH, check_box)))  # 等待全选框加载完毕
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
                    WebDriverWait(self.driver, 10, 0.001).until(
                        EC.presence_of_element_located((By.XPATH, address))).click()
                # 点击提交按钮
                WebDriverWait(self.driver, 10, 0.001).until(EC.presence_of_element_located((By.XPATH, submit))).click()
                break
            if (self.buy_time - now_time) > self.time_remaining:
                sleep(3)

    # 付款函数
    def pay(self, input_box=None, enter=None, click_to_pay=None, switch_frame=None):
        """
        :param input_box: 传入密码输入框Xpath
        :param enter: 默认为空,传入确认付款按钮Xpath
        :param click_to_pay: 默认为空,传入点击去付款调出输入框按钮Xpath
        :param switch_frame: 默认为空,切换frame框架
        """
        if click_to_pay is None:
            pass
        else:
            # 点击支付按钮
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, click_to_pay))).click()
        if input_box is None:
            pass
        else:
            if self.password is None or len(self.password) != 6:
                pass
            else:
                if switch_frame is None:
                    pass
                else:
                    # 切换frame框架
                    WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, switch_frame)))
                    self.driver.switch_to.frame(self.driver.find_element(By.XPATH, switch_frame))
                # 等待输入框加入BOM树
                WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, input_box))).click()
                for i in self.password:
                    typewrite(i)
                if enter is None:
                    press('enter')
                else:
                    WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, enter))).click()
                sleep(10)
                self.driver.quit()  # 退出浏览器函数

    # 淘宝函数
    def taobao(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://cart.taobao.com/cart.htm',
                          '/html/body/div[3]/div[2]/div[2]/div[2]/div[5]/div/div[2]/div[2]/div/a[1]',
                          '//*[@id="login"]/div[1]/i')
        else:
            self.account_login('https://cart.taobao.com/cart.htm',
                               '//*[@id="J_MyAlipayInfo"]/span/a',
                               '//*[@id="fm-login-id"]', '//*[@id="fm-login-password"]',
                               '//*[@id="login-form"]/div[4]/button')
        self.check('//*[@id="J_SelectAll1"]/div/label')
        self.seckill('//*[@id="J_Go"]', '//*[@id="submitOrderPC_1"]/div[1]/a[2]')
        self.pay('//*[@id="payPassword_rsainput"]', '//*[@id="validateButton"]',
                 switch_frame='//*[@id="channels"]/div/iframe')

    # 京东函数
    def jd(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://cart.jd.com/cart_index', '//*[@id="J_user"]/div/div[1]/div[2]/p[2]/a[2]')
        else:
            self.account_login('https://cart.jd.com/cart_index', '//*[@id="J_user"]/div/div[1]/div[2]/p[2]/a[2]',
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
            self.qr_login('https://shopping.suning.com/cart.do#resize:380,450',
                          '/html/body/div[8]/div[3]/div[1]/div[3]/div[2]/div[5]/a')
        else:
            self.account_login('https://shopping.suning.com/cart.do#resize:380,450',
                               '/html/body/div[8]/div[3]/div[1]/div[3]/div[2]/div[5]/a',
                               '//*[@id="userName"]', '//*[@id="password"]',
                               '//*[@id="submit"]', '/html/body/div[2]/div[1]/div/div[1]/a[2]')
        self.check('//*[@id="chooseAllCheckFrame2"]')
        self.seckill('//*[@id="cart-wrapper"]/div[3]/div/div/div[2]/div[2]/a', '//*[@id="submit-btn"]')

    # vivo函数
    def vivo(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://shop.vivo.com.cn/shoppingcart', '/html/body/div[1]/div[3]/div[1]/div[3]/div[1]',
                          '/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/img[2]')
        else:
            self.account_login('https://shop.vivo.com.cn/shoppingcart', '/html/body/div[1]/div[3]/div[1]/div[3]/div[1]',
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
                          '//*[@id="root"]/div/div[3]/div/div[2]/div/div[1]/div[2]')
        else:
            self.account_login('https://www.opposhop.cn/cn/web/cart', '//*[@id="root"]/div/div[1]/div/div[2]/div[3]',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/div/div/div/div/input',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div/div/div[1]/input',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div[4]',
                               '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/span')
        self.check('//*[@id="input-36"]')
        self.seckill('//*[@id="app"]/div/div[1]/main/div/div[2]/div/div[1]/div[3]/button',
                     '//*[@id="app"]/div/div[1]/div/main/div/div[8]/div/div/div[3]/button')

    # 小米函数
    def xiaomi(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://www.mi.com/shop/buy/cart', '//*[@id="root"]/div/div/div[1]/div[2]/span/span',
                          '//*[@id="root"]/div/div/div[2]/div/div/div[2]/div/div[1]/div[1]')
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
                     '//*[@id="app"]/div[2]/div/div/div[2]/div/div[6]/div[2]/div/a[1]',
                     '//*[@id="app"]/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]')
        self.pay(click_to_pay='//*[@id="app"]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/ul/li[1]/img')

    # 华为函数
    def huawei(self):
        if self.login_selection == 'qr_code':
            self.qr_login('https://www.vmall.com/cart', '//*[@id="logoutUrl"]/span/span')
        else:
            self.account_login('https://www.vmall.com/cart', '//*[@id="logoutUrl"]/span/span',
                               '/html/body/div/div/div[1]/div[3]/div[3]/span[3]/div[1]/form/div[2]/div/div/div/input',
                               '/html/body/div/div/div[1]/div[3]/div[3]/span[3]/div[1]/form/div[3]/div/div/div/input',
                               '/html/body/div/div/div[1]/div[3]/div[3]/span[3]/div[1]/div[2]/div/div/div')
        self.check('//*[@id="app"]/div[2]/div[3]/div[4]/div/div[1]/label/input',
                   '//*[@id="app"]/div[2]/div[3]/div[1]/a', '//*[@id="ecBoxID"]/div[2]/div[3]/a[2]')
        self.seckill('//*[@id="app"]/div[2]/div[3]/div[4]/div/div[2]/a', '//*[@id="checkoutSubmit"]')
        self.pay(click_to_pay='/html/body/div[1]/div/div/ul/li/button')


if __name__ == '__main__':
    # 实例化对象
    Spike = SpikeSystem_window()
    Spike.mainloop()  # 显示窗口
