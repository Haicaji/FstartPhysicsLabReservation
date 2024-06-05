from SeatReservationSystem.UserSystem import UserSystem
from SeatReservationSystem.RequestExecutor import RequestExecutor

import os
import re

from multiprocessing import Process

User_dir = "./Data/User/"
SeatSystem_dir = "./Data/SeatSystem/"
room_file = "./Data/SeatSystem/room_and_seats_id.json"
teacher_file = "./Data/SeatSystem/teachers_id.json"


# 启动预约
def run_request_system():
    user_dir_files = os.listdir(User_dir)
    # 等待用户确认
    input("回车开始预约")
    process = []
    for user_file in user_dir_files:
        p = Process(target=run_request_system_sub_process, args=(user_file,))
        process.append(p)
        p.start()

    for p in process:
        p.join()

    print("-----------预约结束-----------")


# 预约子进程
def run_request_system_sub_process(user_file):
    request_executor = RequestExecutor(
        f"{User_dir}{user_file}", room_file, teacher_file
    )


# 添加用户
def run_user_system():
    print("-----------用户系统-----------")
    print("1. 新建用户")
    print("2. 修改用户")
    print("3. 删除用户")
    print("4. 退出")
    while True:
        while True:
            try:
                choice_user_system = int(input("请选择功能序号: "))
                if 1 <= choice_user_system <= 4:
                    break
            except:
                pass
            print("输入非法请重新输入: ", end="")

        if choice_user_system == 1:
            print("-----------新建用户-----------")
            user_dir_files = [
                str_.replace(".json", "") for str_ in os.listdir(User_dir)
            ]
            # 输入用户名
            print("请输入用户名: ", end="")
            while True:
                user_name = input()
                if re.match(r"^\w+$", user_name):
                    break
                else:
                    print("用户名只能包含字母、数字和下划线，请重新输入: ", end="")
            # 创建UserSystem类
            user = UserSystem(
                f"{User_dir}{user_name}.json",
                room_file,
                teacher_file,
            )
            # 填入学号密码
            student_id = input("输入学号: ")
            passwd = input("输入密码: ")
            user.set_student_info(student_id, passwd)
            # 是否添加预约
            while True:
                print("是否添加预约: ")
                print("1. 是")
                print("其他. 否")
                choice_add = input()
                if choice_add == "1":
                    user.add_unbooked()
                    print("----------------------")
                    print("添加成功, 目前信息如下:")
                    user.display_user_data()
                else:
                    break
        elif choice_user_system == 2:
            print("-----------修改用户-----------")
            user_dir_files = [
                str_.replace(".json", "") for str_ in os.listdir(User_dir)
            ]
            print("有如下用户")
            for index, user_file in enumerate(user_dir_files):
                print(f"{index + 1}: {user_file.replace('.json', '')}")
            print("请选择要修改的用户: ")
            while True:
                try:
                    user_index = int(input("输入用户序号: ")) - 1
                    if 0 <= user_index < len(user_dir_files):
                        break
                except:
                    pass
                print("输入非法请重新输入: ", end="")
            user_name = user_dir_files[user_index]
            # 创建UserSystem类
            user = UserSystem(
                f"{User_dir}{user_name}.json",
                room_file,
                teacher_file,
            )
            # 请选择功能
            while True:
                print("请选择对预约的操作:")
                print("1. 添加")
                print("2. 删除")
                print("其他. 退出")
                choice_add = input()
                if choice_add == "1":
                    user.add_unbooked()
                    print("----------------------")
                    print("添加成功, 目前信息如下:")
                    user.display_user_data()
                elif choice_add == "2":
                    user.delete_unbooked()
                    print("----------------------")
                    print("删除成功, 目前信息如下:")
                    user.display_user_data()
                else:
                    break
        elif choice_user_system == 3:
            print("-----------删除用户-----------")
            # 获取用户目录所有文件
            user_dir_files = os.listdir(User_dir)
            if len(user_dir_files) == 0:
                print("没有用户可删除")
                continue
            print("有如下用户")
            for index, user_file in enumerate(user_dir_files):
                print(f"{index+1}: {user_file.replace('.json', '')}")
            print("请选择要删除的用户: ")
            while True:
                try:
                    user_index = int(input("输入用户序号: ")) - 1
                    if 0 <= user_index < len(user_dir_files):
                        break
                except:
                    pass
                print("输入非法请重新输入: ", end="")
            # 删除文件
            try:
                os.remove(User_dir + user_dir_files[user_index])
                print("删除成功")
            except:
                print("删除失败")
        else:
            return
        print("---------再次进入用户系统---------")
        print("1. 新建用户")
        print("2. 修改用户")
        print("3. 删除用户")
        print("4. 退出")


if __name__ == "__main__":
    print("---------欢迎使用座位预约主系统---------")
    print("1. 用户系统")
    print("2. 抢座系统")
    print("3. 退出")
    while True:
        while True:
            try:
                choice = int(input("请选择功能序号: "))
                if 1 <= choice <= 3:
                    break
            except:
                pass
            print("输入非法请重新输入: ", end="")

        if choice == 1:
            run_user_system()
        elif choice == 2:
            run_request_system()
        else:
            exit()
        print("---------再次进入座位预约主系统---------")
        print("1. 用户系统")
        print("2. 抢座系统")
        print("3. 退出")
