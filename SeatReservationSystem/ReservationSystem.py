import json
import random
import re

import requests
from fake_useragent import UserAgent


class ReservationSystem:
    def __init__(self, student_id, passwd):
        # 传入参数
        self.student_id = student_id
        self.passwd = passwd
        # 临时参数
        self.session = ""
        self.viewstate = ""
        self.header = {
            "Host": "",
            "Accept": "",
            "User-Agent": f"{UserAgent().random}",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": f"Cookie: COOKIES_KEY_USERNAME={self.student_id}; login=",
            "Connection": "close",
        }
        self.sub_book_system_code = ""
        # 长期参数
        self.room_and_seats_id = {}
        # room_and_seats_id = {"room_name":{"id": "","seat": {"seat_name": [id, state]}
        self.teachers_id = {}
        # teachers_id = [{"teacher_name": teacher_id}]
        self.all_book = [{}]
        # all_book = [{"book_id": "", "room": "", "name": "", "date": "", "start": "", "end": "", "state": ""}}

    # 登入预约系统-总方法
    def login(self):
        self.__get_session()
        self.__login_main_system()
        self.__get_sub_system_code()
        self.__login_sub_book_system()

    # 请求登入页面得到session, __VIEWSTATE, 子系统code
    def __get_session(self):
        host = "aryun.ustcori.com:4540"
        url = f"http://{host}/Page/BI/BI000.aspx"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
            "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        )
        # GET请求
        response = requests.get(url, headers=header)
        # 获取session
        self.session = re.search(
            r"(?<=ASP.NET_SessionId=).*?(?=;)", response.headers["Set-Cookie"]
        )
        # 检测是否获取session成功
        if self.session:
            self.session = self.session.group()
        else:
            Exception("获取session失败")
        # 获取__VIEWSTATE
        self.viewstate = re.search(
            r'(?<=<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value=").*?(?=" />)',
            response.text,
        )
        # 检测是否获取__VIEWSTATE成功
        if self.viewstate:
            self.viewstate = self.viewstate.group()
        else:
            Exception("获取__VIEWSTATE失败")

    # 登入主系统
    def __login_main_system(self):
        host = "aryun.ustcori.com:4540"
        url = f"http://{host}/Page/BI/BI000.aspx"
        # 将session存入header
        self.header["Cookie"] += f"; ASP.NET_SessionId={self.session}"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
            "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        )
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": self.viewstate,
            "hidUserID": "",
            "hidUserPassWord": "",
            "hidLogincount": "",
            "isCanlogin": "1",
            "txtUserID": self.student_id,
            "txtEditUserID": "",
            "txtOldPassWord": "",
            "txtNewPassWord": "",
            "txtConfirmPassWord": "",
            "txtUsername": self.student_id,
            "txtPassword": self.passwd,
            "btnLogin.x": f"{random.randint(45, 100)}",
            "btnLogin.y": f"{random.randint(15, 50)}",
        }
        # POST请求登入
        response = requests.post(url, headers=header, data=data)
        # 判断主系统是否登入成功
        if response.status_code != 302:
            Exception("主系统登入失败")

    # 获取子系统code
    def __get_sub_system_code(self):
        host = "aryun.ustcori.com:4540"
        url = f"http://{host}/Page/BI/BI0000.aspx"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Cache-Control"] = "max-age=0"
        header["Accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
            "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        )
        # GET请求
        response = requests.get(url, headers=header)
        # 获取子系统code
        self.sub_book_system_code = re.search(
            r'(?<=<a href="http://aryun.ustcori\.com:4545/Login\.aspx\?code=).+(?=" style="float: left">)',
            response.text,
        )
        # 检测是否获取子系统code成功
        if self.sub_book_system_code:
            self.sub_book_system_code = self.sub_book_system_code.group()
        else:
            Exception("获取子系统code失败")

    # 登入实验室预约子系统
    def __login_sub_book_system(self):
        host = "aryun.ustcori.com:4545"
        url = f"http://{host}/LMWeb/LM00/index.ashx?Method=Login&t={random.random()}"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["Content-Type"] = "application/x-www-form-urlencoded"
        # 请求数据
        data = {
            "username": "",
            "password": "d41d8cd98f00b204e9800998ecf8427e",
            "checkCode": self.sub_book_system_code,
            "flag": "1",
        }
        # POST请求
        response = requests.post(url, headers=header, data=data)
        # 检测是否登入成功
        if json.loads(response.text)["Flag"][0]["Status"] != "1":
            Exception("实验室预约子系统登入失败")

    # 获取实验室及其座位序列号
    def get_room_and_seats_id(self):
        host = "aryun.ustcori.com:4545"
        url = f"http://{host}/LMWeb/LM21/HLM211700.ashx?Method=LoadShiYanShiTree&t={random.random()}"
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        # POST请求
        response = requests.post(url, headers=header)
        # 检测是否获取实验室及其座位序列号成功
        if response.status_code != 200:
            Exception("获取实验室及其座位序列号失败")
        # 获取实验室及其座位序列号
        response_json = json.loads(response.text)
        for room in response_json:
            room_name = room["text"]
            self.room_and_seats_id[room_name] = {}
            self.room_and_seats_id[room_name]["id"] = room["id"]
            self.room_and_seats_id[room_name]["seat"] = {}
            if "children" in room:
                for a in room["children"]:
                    seat_name = a["text"]
                    self.room_and_seats_id[room_name]["seat"][seat_name] = [
                        a["id"],
                        a["state"],
                    ]

    # 获取当前座位预约情况
    def get_seat_state(self, seat_id, start_date, end_date):
        host = "aryun.ustcori.com:4545"
        url = (
            f"http://{host}/LMWeb/LM21/HLM211700.ashx?Method=InitCalendarByZuoWeiID"
            f"&KaiShiRiQi={start_date}&JieShuRiQi={end_date}&t={random.random()}"
        )
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["Content-Type"] = "application/x-www-form-urlencoded"
        data = {
            "showdate": start_date,
            "viewtype": "week",
            "timezone": "8",
            "mode": "0",
            "MeetingId": seat_id,
            "YuYueID": "",
        }
        # POST请求
        response = requests.post(url, headers=header, data=data)
        # 检测是否获取当前座位预约情况成功
        if response.status_code != 200:
            Exception("获取当前座位预约情况失败")
        # 获取当前座位预约情况
        booked_time = {}
        for state in json.loads(response.text)["events"]:
            data = re.search(r"\d\d\d\d-\d\d-\d\d", state[2]).group()
            start_time = re.search(
                r"(?<=\d\d\d\d-\d\d-\d\d )\d\d:\d\d", state[2]
            ).group()
            end_time = re.search(r"(?<=\d\d\d\d-\d\d-\d\d )\d\d:\d\d", state[3]).group()
            if data not in booked_time:
                booked_time[data] = [[start_time, end_time]]
            else:
                booked_time[data].append([start_time, end_time])

        return booked_time

    # 获取老师id
    def get_teachers_id(self):
        teachers_row = 50
        host = "aryun.ustcori.com:4545"
        url = (
            f"http://{host}/LMWeb/LM00/HLM000103.ashx?Method=GetUsersTableGrid&t={random.random()}"
            f"&Type=0&XingMing=&DengLuMing=&XingBie=&SuoShuYuanXi=&page=1&rows={teachers_row}"
        )
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["Content-Type"] = "application/x-www-form-urlencoded"
        # Get请求
        response = requests.get(url, headers=header)
        # 检测是否获取老师id成功
        if response.status_code != 200:
            Exception("获取老师id失败")
        # 获取老师id
        self.teachers_id = {}
        for teacher in json.loads(response.text)["rows"]:
            if teacher["XingMing"] != "001":
                self.teachers_id[teacher["XingMing"]] = teacher["YongHuID"]

    # 获取位置当前时段是否可以预约
    def book_seat_before(self, seat_id, date, start_time, end_time):
        host = "aryun.ustcori.com:4545"
        url = f"http://{host}/LMWeb/LM21/HLM211700.ashx?Method=JudgeYuYueChongTu&t={random.random()}"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["Content-Type"] = "application/x-www-form-urlencoded"
        # POST请求
        data = {
            "Action": "check",
            "KaiFangShiJianID": "",
            "ZuoWeiID": seat_id,
            "KaiShiRiQi": date,
            "JieShuRiQi": date,
            "KaiShiShiJian": start_time,
            "JieShuShiJian": end_time,
            "ZhouCiArray": "0,1,2,3,4,5,6",
            "EditYuYueID": "",
        }
        response = requests.post(url, headers=header, data=data)
        # 检测是否返回成功
        if response.status_code != 200:
            Exception("获取位置当前时段是否可以预约失败")
        # 检测是否可以预约
        status = json.loads(response.text)["Flag"][0]["Status"]
        if status == "1":
            return True
        elif status == "2":
            return "The time is not allowed"
        elif status == "3":
            return "booked by others"
        elif status == "4":
            return "waiting"
        elif status == "5":
            return "Time conflict with yourself"
        else:
            return False

    # 预约座位
    def book_seat(self, seat_id, date, start_time, end_time, teacher_id):
        host = "aryun.ustcori.com:4545"
        url = f"http://{host}/LMWeb/LM21/HLM211700.ashx?Method=JudgeYuYueChongTu&t={random.random()}"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["Content-Type"] = "application/x-www-form-urlencoded"
        # POST请求
        data = {
            "Action": "add",
            "KaiFangShiJianID": "",
            "NeiRong": "",
            "ZuoWeiID": seat_id,
            "KaiShiRiQi": date,
            "JieShuRiQi": date,
            "KaiShiShiJian": start_time,
            "JieShuShiJian": end_time,
            "ZhouCiArray": "0",
            "EditYuYueID": "",
            "ZhiDaoJiaoShiID": teacher_id,
        }
        # POST请求
        response = requests.post(url, headers=header, data=data)
        # 检测是否预约请求成功
        if response.status_code != 200:
            Exception("预约座位请求失败")
        # 检测是否可以预约成功
        status = json.loads(response.text)["Flag"][0]["Status"]
        if status == "1":
            return True
        elif status == "2":
            return "waiting"
        elif status == "3":
            return "booked by others"
        else:
            return False

    # 获取当前所有预约
    def get_all_book(self):
        id_row = 50
        host = "aryun.ustcori.com:4545"
        url = f"http://{host}/LMWeb/LM21/HLM211900.ashx?Method=GetYueYuList&t={random.random()}&page=1&rows={id_row}"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["Content-Type"] = "application/x-www-form-urlencoded"
        # POST请求
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            Exception("获取当前所有预约请求失败")
        for book_block in json.loads(response.text)["rows"]:
            book_block_new = {
                "book_id": book_block["YuYueID"],
                "room": f'{book_block["MenName"]} {book_block["ShiYanShiMingCheng"]}',
                "name": book_block["ShiYanMingCheng"],
                "date": book_block["KaiShiRiQi"],
                "start": book_block["KaiShiShiJian"],
                "end": book_block["JieShuShiJian"],
                "state": book_block["ZhuangTaiMengCheng"],
            }
            self.all_book.append(book_block_new)

    # 取消预约
    def cancel_book(self, book_id):
        host = "aryun.ustcori.com:4545"
        url = f"http://{host}/LMWeb/LM21/HLM211900.ashx?Method=DeleteYuYue&t={random.random()}"
        # 修改请求头
        header = self.header
        header["Host"] = host
        header["Accept"] = "application/json, text/javascript, */*"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["Content-Type"] = "application/x-www-form-urlencoded"
        # POST请求
        data = {
            "YuYueID": book_id,
        }
        response = requests.post(url, headers=header, data=data)
        if response.status_code != 200:
            Exception("取消预约请求失败")
        if json.loads(response.text)["Flag"][0]["Status"] == "1":
            return True
        else:
            return False
