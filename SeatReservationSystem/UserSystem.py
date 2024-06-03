import json
import os
import random


class UserSystem:
    def __init__(self, user_file, room_file, teacher_file):
        self.user_file = user_file
        self.room_file = room_file
        self.teacher_file = teacher_file

        if not os.path.exists(self.user_file):
            self.create_user_file()

    def create_user_file(self):
        user_data = {
            "student_id": "",
            "passwd": "",
            "unbooked": [],
            "booked_success": [],
            "booked_fail": [],
        }
        with open(self.user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)

    def set_student_info(self, student_id, passwd):
        with open(self.user_file, "r+", encoding="utf-8") as f:
            user_data = json.load(f)
            user_data["student_id"] = student_id
            user_data["passwd"] = passwd
            f.seek(0)
            json.dump(user_data, f, ensure_ascii=False, indent=4)
            f.truncate()

    def add_unbooked(self):
        with open(self.room_file, "r", encoding="utf-8") as rf, open(
            self.teacher_file, "r", encoding="utf-8"
        ) as tf:
            rooms = json.load(rf)
            teachers = json.load(tf)

        print("请选择预约模式:")
        modes = ["默认预约", "固定位置预约", "固定时间预约"]
        for i, mode in enumerate(modes):
            print(f"{i + 1}. {mode}")
        mode_index = int(input("输入预约模式序号: ")) - 1
        selected_mode = modes[mode_index]

        unbooked_entry = {"mode": selected_mode}

        print("\n请选择老师:")
        teacher_names = list(teachers.keys())
        for i, teacher_name in enumerate(teacher_names):
            print(f"{i + 1}. {teacher_name}")
        print(f"{len(teacher_names) + 1}. 随机指派")
        teacher_index = int(input("输入老师序号: ")) - 1
        if teacher_index == len(teacher_names):
            selected_teacher = random.choice(teacher_names)
        else:
            selected_teacher = teacher_names[teacher_index]

        teacher_id = teachers[selected_teacher]

        unbooked_entry.update(
            {"teacher_name": selected_teacher, "teacher_id": teacher_id}
        )

        with open(self.user_file, "r+", encoding="utf-8") as f:
            user_data = json.load(f)
            user_data["unbooked"].append(unbooked_entry)
            f.seek(0)
            json.dump(user_data, f, ensure_ascii=False, indent=4)
            f.truncate()

    def display_user_data(self):
        with open(self.user_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)
            print(json.dumps(user_data, ensure_ascii=False, indent=4))
