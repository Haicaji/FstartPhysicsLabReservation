import json
import os
import random
import re
from datetime import datetime, timedelta


class UserSystem:
    def __init__(self, user_file, room_file, teacher_file):
        self.user_file = user_file  # 用户配置文件路径
        self.room_file = room_file  # 实验室配置文件路径
        self.teacher_file = teacher_file  # 教师配置文件路径
        # 不存在用户配置文件时创建
        if not os.path.exists(self.user_file):
            self.__create_user_file()

    # 初始化用户配置文件
    def __create_user_file(self):
        user_data = {
            "student_id": "",
            "passwd": "",
            "book_begin_time": "00:00",
            "unbooked": [],
            "booked_success": [],
            "booked_fail": [],
        }
        with open(self.user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)

    # 配置用户名和密码
    def set_student_info(self, student_id, passwd):
        with open(self.user_file, "r+", encoding="utf-8") as f:
            user_data = json.load(f)
            user_data["student_id"] = student_id
            user_data["passwd"] = passwd
            f.seek(0)
            json.dump(user_data, f, ensure_ascii=False, indent=4)
            f.truncate()

    # 添加预约模块
    def add_unbooked(self):
        try:
            with open(self.room_file, "r", encoding="utf-8") as rf, open(
                self.teacher_file, "r", encoding="utf-8"
            ) as tf:
                rooms = json.load(rf)
                teachers = json.load(tf)
        except:
            print("缺少文件,无法增加预约")
            return

        unbooked_block = UserBlock(rooms, teachers).output_block()

        with open(self.user_file, "r+", encoding="utf-8") as f:
            user_data = json.load(f)
            user_data["unbooked"].append(unbooked_block)
            f.seek(0)
            json.dump(user_data, f, ensure_ascii=False, indent=4)
            f.truncate()

    # 删除预约模块
    def delete_unbooked(self):
        with open(self.user_file, "r+", encoding="utf-8") as f:
            user_data = json.load(f)
            # 显示所有book_block
            for index, book_block in enumerate(user_data["unbooked"]):
                print(f"{index + 1}:")
                print(json.dumps(book_block, ensure_ascii=False, indent=4))
            # 选择要删除的book_block
            try:
                index = int(input("请输入要删除的预约模块序号(错误输入即取消删除): ")) - 1
            except:
                print("取消删除")
                return
            if index < 0 or index >= len(user_data["unbooked"]):
                print("取消删除")
                return
            user_data["unbooked"].pop(index)
            f.seek(0)
            json.dump(user_data, f, ensure_ascii=False, indent=4)
            f.truncate()

    # 显示所有数据
    def display_user_data(self):
        with open(self.user_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)
            print(json.dumps(user_data, ensure_ascii=False, indent=4))


class UserBlock:
    def __init__(self, rooms, teachers):
        self.rooms = rooms
        self.teachers = teachers
        # block数据
        self.mode = ""
        self.teacher_name = ""
        self.teacher_id = ""

        self.seat_id = ""
        self.room_name = ""
        self.seat_name = ""
        self.date = ""
        self.time_range = []

        self.main()

    # 返回生成的UserBlock字典
    def output_block(self):
        return dict(
            mode=self.mode,
            seat_id=self.seat_id,
            room_name=self.room_name,
            seat_name=self.seat_name,
            date=self.date,
            time_range=self.time_range,
            teacher_name=self.teacher_name,
            teacher_id=self.teacher_id,
        )

    def main(self):
        self.__choose_mode()
        self.__choose_teacher()
        if self.mode == "默认模式":
            self.__default_mode()
        elif self.mode == "抢位置模式":
            self.__rob_seat()
        elif self.mode == "固定时间模式":
            self.__brush_time()

    # 选择模式
    def __choose_mode(self):
        # 选择模式
        modes = ["默认模式", "抢位置模式", "固定时间模式"]
        print("请选择预约模式: ")
        for i, mode in enumerate(modes):
            print(f"{i + 1}: {mode}")
        print("输入预约模式序号: ", end="")
        while True:
            mode_index = int(input()) - 1
            if 0 <= mode_index < len(modes):
                break
            print("输入非法请重新输入: ", end="")
        self.mode = modes[mode_index]

    # 选择老师
    def __choose_teacher(self):
        print("\n请选择老师: ")
        teacher_names = list(self.teachers.keys())
        print(f"0: 随机指派")
        # 输出老师信息
        self.__output_list(teacher_names)
        print("输入老师序号: ", end="")
        while True:
            teacher_index = int(input()) - 1
            if teacher_index == -1:
                selected_teacher = random.choice(teacher_names)
                print(f"随机选择老师为 {selected_teacher}")
                break
            elif 0 <= teacher_index < len(teacher_names):
                selected_teacher = teacher_names[teacher_index]
                break
            print("输入非法请重新输入: ", end="")
        self.teacher_name = selected_teacher
        self.teacher_id = self.teachers[selected_teacher]

    # 输出列表信息
    def __output_list(self, show_list):
        max_length = max(len(name) for name in show_list) + 2  # 确保每个名字有相同的宽度
        for i in range(0, len(show_list), 2):
            left = f"{i + 1}: {show_list[i]}".ljust(max_length)
            if i + 1 < len(show_list):
                right = f"{i + 2}: {show_list[i + 1]}"
            else:
                right = ""
            print(left + right)

    # 校验日期
    def __validate_date(self, date_str):
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            year, month, day = map(int, date_str.split("-"))
            if 1 <= month <= 12:
                if 1 <= day <= 31:  # 粗略判断
                    return True
        return False

    # 获取日期
    def __get_date(self, date_str):
        """
        根据输入的日期字符串返回相应的日期

        参数:
            date_str (str_): 输入的日期字符串

        返回:
            str_: 转换后的日期字符串，格式为 YYYY-MM-DD
        """
        today = datetime.today()
        if date_str == "":
            return today.strftime("%Y-%m-%d")
        elif date_str == "t" or date_str == "T":
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_str == "a" or date_str == "A":
            return (today + timedelta(days=2)).strftime("%Y-%m-%d")
        return date_str

    # 校验时间
    def __validate_time(self, time_str):
        """
        校验时间格式是否为 HH:MM

        参数:
            time_str (str_): 需要校验的时间字符串

        返回:
            bool: 如果格式正确返回 True，否则返回 False
        """
        pattern = r"^\d{2}:\d{2}$"
        if re.match(pattern, time_str):
            hour, minute = map(int, time_str.split(":"))
            if 0 <= hour < 24 and 0 <= minute < 60:
                return True
        return False

    # 校验时间段
    def __validate_time_range(self, start_time, end_time):
        """
        校验时间段是否合法

        参数:
            start_time (str_): 开始时间
            end_time (str_): 结束时间

        返回:
            bool: 如果时间段合法返回 True，否则返回 False
        """
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))
        # 判断时间段的切分点
        if start_minute not in {0, 30} or end_minute not in {0, 30}:
            print("时间段不合法, 请检查时间段的切分点")
            return False

        time_range = (end_hour - start_hour) * 60 + (end_minute - start_minute)

        max_time_range = 1 * 60 + 0  # hour = 1, minute = 0
        min_time_range = 1 * 60 + 0  # hour = 1, minute = 0

        # 判断时间段的长度
        if time_range < min_time_range or time_range > max_time_range:
            print("时间段不合法, 请检查时间段的长度")
            return False

        return True

    # 获取时间段
    def __get_time_range(self, time_range_str):
        """
        根据输入的时间段字符串返回相应的时间段

        参数:
            time_range_str (str_): 输入的时间段字符串

        返回:
            str_: 转换后的时间段字符串，格式为 HH:MM-HH:MM
        """
        if "-" not in time_range_str:
            return False

        [start_time, end_time] = time_range_str.split("-")
        if not (self.__validate_time(start_time) or self.__validate_time(end_time)):
            return False

        if not self.__validate_time_range(start_time, end_time):
            return False

        return start_time + "-" + end_time

    # 校验座位
    def __validate_seat(self, seat_str):
        seat = seat_str.replace(" ", "")
        seat = seat.split(",")
        seat = list(filter(None, seat))
        seat = [s.split("-") for s in seat]
        seat_id = []
        for seat_range in seat:
            # 删除空值
            seat_range = list(filter(None, seat_range))
            try:
                seat_range = [int(i) for i in seat_range]
            except:
                return False

            if len(seat_range) == 2:
                if seat_range[0] >= seat_range[1]:
                    return False
                seat_id += list(range(seat_range[0], seat_range[1] + 1))
            else:
                seat_id.append(seat_range[0])

        # 去重
        seat_id = list(set(seat_id))
        # 按从小到大排序
        seat_id.sort()

        return seat_id

    # 默认模式
    def __default_mode(self):
        # 选择实验室
        rooms_name = list(self.rooms.keys())
        print("\n请选择实验室: ")
        self.__output_list(rooms_name)
        print("输入实验室序号: ", end="")
        while True:
            while True:
                try:
                    room_index = int(input()) - 1
                    if 0 <= room_index < len(self.rooms):
                        break
                except:
                    pass
                print("输入非法请重新输入: ", end="")
            self.room_name = rooms_name[room_index]

            seat_names = list(self.rooms[self.room_name]["seat"].keys())
            if len(seat_names) != 0:
                break
            print("该实验室没有座位, 请重新选择: ", end="")

        # 选择座位
        print("\n请选择座位: ")
        self.__output_list(seat_names)
        print("输入座位序号: ", end="")
        while True:
            try:
                seat_index = int(input()) - 1
                if 0 <= seat_index < len(seat_names):
                    break
            except:
                pass
            print("输入非法请重新输入: ", end="")
        self.seat_name = seat_names[seat_index]
        self.seat_id = self.rooms[self.room_name]["seat"][self.seat_name][0]

        # 选择日期
        date = self.__get_date(input("输入日期 (格式: YYYY-MM-DD，回车为今天，t为明天，a为后天): "))
        while not self.__validate_date(date):
            print("日期格式不正确，请重新输入。")
            date = self.__get_date(input("输入日期 (格式: YYYY-MM-DD，回车为今天，t为明天，a为后天): "))
        self.date = date
        # 选择时间段
        time_range = self.__get_time_range(input("输入时间段 (格式: HH:MM-HH:MM): "))
        while not time_range:
            print("时间段格式不正确，请重新输入。")
            time_range = self.__get_time_range(input("输入时间段 (格式: HH:MM-HH:MM): "))
        self.time_range = time_range

    # 抢位置模式
    def __rob_seat(self):
        pass

    # 固定时间模式
    def __brush_time(self):
        # 选择日期
        # noinspection DuplicatedCode
        date = self.__get_date(input("输入日期 (格式: YYYY-MM-DD，回车为今天，t为明天，a为后天): "))
        while not self.__validate_date(date):
            print("日期格式不正确，请重新输入。")
            date = self.__get_date(input("输入日期 (格式: YYYY-MM-DD，回车为今天，t为明天，a为后天): "))
        self.date = date
        # 选择时间段
        time_range = self.__get_time_range(input("输入时间段 (格式: HH:MM-HH:MM): "))
        while not time_range:
            print("时间段格式不正确，请重新输入(格式: HH:MM-HH:MM): ", end="")
            time_range = self.__get_time_range(input())
        self.time_range = time_range

        # 选入实验室及其位置
        choose_rooms_name = []
        choose_seats_name = []
        choose_seats_id = []
        # 选择实验室
        rooms_name = list(self.rooms.keys())
        while True:
            # 选择实验室
            print("\n请选入实验室: ")
            self.__output_list(rooms_name)
            print("输入实验室序号(输入0或者直接回车结束选入): ", end="")
            while True:
                while True:
                    try:
                        room_index = int(input()) - 1
                        if -1 <= room_index < len(self.rooms):
                            if room_index == -1 and len(choose_rooms_name) == 0:
                                print("座位列表为空请选择: ", end="")
                            else:
                                break
                        print("输入非法请重新输入: ", end="")
                    except:
                        room_index = -1
                        break

                if room_index == -1:
                    break
                choose_rooms_name.append(rooms_name[room_index])
                seat_names = list(self.rooms[rooms_name[room_index]]["seat"].keys())
                if len(seat_names) != 0:
                    break
                print("该实验室没有座位, 请重新选择: ", end="")
            if room_index == -1:
                break

            # 选择座位
            print("\n请选择座位: ")
            self.__output_list(seat_names)
            print("输入座位序号(可采用1-3,5-9的形式): ", end="")
            while True:
                seat_index = self.__validate_seat(input())
                if seat_index:
                    seat_index = [i - 1 for i in seat_index]
                    for i in seat_index:
                        if not 0 <= i < len(seat_names):
                            seat_index = False
                            break
                    if seat_index:
                        break
                print("输入非法请重新输入: ", end="")

            choose_seats_name.append(seat_names[seat_index[0]])
            choose_seats_id.append(
                self.rooms[rooms_name[room_index]]["seat"][seat_names[seat_index[0]]][0]
            )
            for index in seat_index[1:]:
                choose_rooms_name.append("-")
                choose_seats_name.append(seat_names[index])
                choose_seats_id.append(
                    self.rooms[rooms_name[room_index]]["seat"][seat_names[index]][0]
                )

        self.seat_id = choose_seats_id
        self.room_name = choose_rooms_name
        self.seat_name = choose_seats_name
