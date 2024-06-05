import json
import random
import threading
import time

from SeatReservationSystem.ReservationSystem import ReservationSystem


class RequestExecutor:
    def __init__(self, json_file, room_file, teacher_file):
        self.teacher_file = teacher_file  # 教师配置文件路径
        self.room_file = room_file  # 实验室配置文件路径
        self.json_file = json_file
        self.user_data = {}
        self.lock = threading.Lock()
        self.__tmp = []  # 多进程的灵活使用变量

        # 读入用户的配置文件数据
        self.load_user_data()
        self.main_execute()

    # 执行请求-主流程
    def main_execute(self):
        # 创建ReservationSystem对象
        reservation_system = ReservationSystem(
            self.user_data["student_id"], self.user_data["passwd"]
        )
        # 登入预约系统
        reservation_system.login()
        # 导入实验室信息
        try:
            with open(self.room_file, "r") as f:
                reservation_system.set_room_and_seats_id = json.load(f)
        except:
            reservation_system.get_room_and_seats_id()
            with open(self.room_file, "w") as f:
                json.dump(reservation_system.room_and_seats_id, f)
        # 导入教师信息
        try:
            with open(self.teacher_file, "r") as f:
                reservation_system.set_teachers_id = json.load(f)
        except:
            reservation_system.get_teachers_id()
            with open(self.teacher_file, "w") as f:
                json.dump(reservation_system.teachers_id, f)

        # 预约座位
        threading_list = []
        for index, user_block in enumerate(self.user_data["unbooked"]):
            # 创建线程
            t = threading.Thread(
                target=self.user_block_threading,
                args=(
                    index,
                    user_block,
                    reservation_system,
                ),
            )
            threading_list.append(t)
            t.start()

        # 等待线程结束
        for t in threading_list:
            t.join()

        for user_block in self.user_data["unbooked"]:
            if user_block["result"] == True:
                del user_block["result"]
                self.user_data["booked_success"].append(user_block)
            else:
                self.user_data["booked_fail"].append(user_block)
            # 在unbooked中删除user_block
            self.user_data["unbooked"].remove(user_block)

        with open(self.json_file, "w") as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)

    # user_block子线程
    def user_block_threading(self, index, user_block, reservation_system):
        # 结果
        result = False
        match user_block["mode"]:
            case "默认模式":
                result = self.default_executor(user_block, reservation_system)
            case "抢位置模式":
                result = self.rob_seat_executor(user_block, reservation_system)
            case "固定时间模式":
                result = self.brush_time_executor(user_block, reservation_system)
        # 结果写入文件
        with self.lock:
            self.user_data["booked_success"][index]["result"] = result

    # 默认模式
    def default_executor(self, user_block, reservation_system):
        result = False
        [start_date, end_date] = [user_block["date"], user_block["date"]]
        [start_time, end_time] = user_block["time_range"].split("-")
        seat_id = user_block["seat_id"]
        teacher_id = user_block["teacher_id"]
        # 判断是否冲突
        booked_time = reservation_system.get_seat_state(seat_id, start_date, end_date)
        if self.is_overlap(user_block["time_range"], booked_time[start_date]):
            return "booked by others"
        # 预约检查
        result = reservation_system.book_seat_before(
            seat_id, start_date, start_time, end_time
        )
        if result == True:
            pass
        elif result == "waiting":
            self.wait_seconds(self.user_data["book_begin_time"])
        else:
            return result
        # 开始预约
        while True:
            result = reservation_system.book_seat(
                seat_id, start_date, start_time, end_time, teacher_id
            )
            if result == True:
                break
            elif result == "waiting":
                time.sleep(0.5)
            else:
                break

        return result

    # 抢位置模式
    def rob_seat_executor(self, user_block, reservation_system):
        result = False
        return result

    # 固定时间模式
    def brush_time_executor(self, user_block, reservation_system):
        result = False
        [date, date] = [user_block["date"], user_block["date"]]
        [start_time, end_time] = user_block["time_range"].split("-")
        teacher_id = user_block["teacher_id"]
        unselect_seat_id_list = user_block["seat_id"]

        while len(unselect_seat_id_list) > 0:
            max_len = 5
            # 随机抽取max个seat_id
            if len(unselect_seat_id_list) < max_len:
                max_len = len(unselect_seat_id_list)
            select_seat_id_list = random.sample(unselect_seat_id_list, max_len)
            self.__tmp = [False for i in range(max_len)]
            threading_list = []
            # 开始预约
            for index, seat_id in enumerate(select_seat_id_list):
                # 创建线程
                t = threading.Thread(
                    target=self.brush_time_executor_simple_reserve,
                    args=(
                        seat_id,
                        date,
                        start_time,
                        end_time,
                        teacher_id,
                        reservation_system,
                        index,
                    ),
                )
                threading_list.append(t)
                t.start()
            # 等待进程结束
            for t in threading_list:
                t.join()

            for r in self.__tmp:
                if r:
                    result = True
                    break
            if result:
                break
            else:
                # 删除已经被选择的
                unselect_seat_id_list = list(
                    set(unselect_seat_id_list) - set(select_seat_id_list)
                )

        return result

    # 固定时间模式的单次预约
    def brush_time_executor_simple_reserve(
        self, seat_id, date, start_time, end_time, teacher_id, reservation_system, index
    ):
        result = False
        # 判断是否冲突
        booked_time = reservation_system.get_seat_state(seat_id, date, date)
        if not self.is_overlap(f"{start_time}-{end_time}", booked_time[date]):
            # 预约检查
            result = reservation_system.book_seat_before(
                seat_id, date, start_time, end_time
            )
            if result == True or result == "waiting":
                if result == "waiting":
                    self.wait_seconds(self.user_data["book_begin_time"])
                # 开始预约
                while True:
                    result = reservation_system.book_seat(
                        seat_id, date, start_time, end_time, teacher_id
                    )
                    if result == True:
                        break
                    elif result == "waiting":
                        time.sleep(0.5)
                    else:
                        result = False
                        break
            else:
                result = False
        with self.lock:
            self.__tmp[index] = result

    # 检查时间段是否与列表中的时间段有重叠
    def is_overlap(self, time_range, time_list):
        """检查时间段是否与列表中的时间段有重叠"""

        def time_to_minutes(time_str):
            """将HH:MM格式的时间转换为分钟数"""
            hours, minutes = map(int, time_str.split(":"))
            return hours * 60 + minutes

        start1, end1 = map(time_to_minutes, time_range.split("-"))

        for time_pair in time_list:
            start2, end2 = map(time_to_minutes, time_pair)
            if max(start1, start2) < min(end1, end2):
                return True
        return False

    # 等待目标时间到达
    def wait_seconds(self, target_time):
        current_time = time.strftime("%H:%M", time.localtime())
        target_hour, target_minute = map(int, target_time.split(":"))
        target_seconds = target_hour * 3600 + target_minute * 60
        current_hour, current_minute = map(int, current_time.split(":"))
        current_seconds = current_hour * 3600 + current_minute * 60
        wait_seconds = target_seconds - current_seconds
        if target_hour == current_hour:
            return
        if wait_seconds < 0:
            wait_seconds += 24 * 3600  # 如果目标时间在当前时间之前，则加一天的秒数
        if wait_seconds - 2 >= 0:
            wait_seconds -= 2
        time.sleep(wait_seconds)

    # 读入用户的配置文件数据
    def load_user_data(self):
        with open(self.json_file, "r") as f:
            self.user_data = json.load(f)
