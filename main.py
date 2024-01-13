import hashlib
import json
import random
import time
import requests


def get_user_input(prompt):
    while True:
        try:
            user_input = int(input(f"{prompt}: ")) - 1
        except ValueError:
            print("🚫 您输入的数据不符合规范！")
            continue
        return user_input


def print_list(obj, is_exit=True):
    if len(obj) == 0:
        return
    print("------------------------------------")
    print("| id | 课程名称")
    index = 1
    for item in obj:
        print("| %2d | %-s" % (index, item['bookName']))
        index = index + 1
    print("------------------------------------")
    if is_exit:
        print("| 退出请输入 -1")
        print("------------------------------------")


def choose_score_range(score_ranges):
    print("------------------------------------")
    print("\n请选择分数范围:")
    for i, score_range in enumerate(score_ranges, 1):
        print(f"{i}. {score_range}分")
    print("------------------------------------")

    score_choice = int(input("选择 1, 2, 或 3: "))
    min_score, max_score = score_ranges[score_choice - 1]
    return min_score, max_score


def made_md5(md5_str):
    hl = hashlib.md5()
    hl.update(md5_str.encode(encoding='utf-8'))
    return hl.hexdigest()


def get_ut(param, param1):

    headers = {
        'contentType': 'application/json',
    }
    response = requests.get(f'http://127.0.0.1:84/ismart/ut?str={param}&i={param1}', headers=headers)
    return response.text


class Login(object):
    def __init__(self, name, password):
        self.session = requests.session()
        self.cookie = None
        self.uid = None
        self.book_id = None

        result = self.login(name, password)
        if result is None:
            return

        task_no = '1'
        courses = self.buy_book()[::-1]
        print_list(courses)
        while True:
            unit_id = get_user_input("单元id")
            if unit_id == -1:
                exit(0)
            if unit_id >= len(courses) or unit_id < 0:
                print("🚫 单元id不存在！")
                continue
            break
        print("\n<%s>" % courses[unit_id]['bookName'])
        self.book_id = courses[unit_id]['bookId']
        name_list, pages = self.tree()
        print_list(name_list)

        while True:
            while True:
                course_id = get_user_input("课程id")
                if course_id == -1:
                    exit(0)
                if course_id >= len(name_list) or course_id < 0:
                    print("🚫 课程id不存在！")
                    continue
                break

            score_ranges = [
                (90, 100),
                (80, 90),
                (70, 80)
            ]

            min_score, max_score = choose_score_range(score_ranges)

            for a in name_list[course_id]['page']:
                for page in pages:
                    if a['Id'] == page['parentId']:
                        score = random.randint(min_score, max_score)
                        self.submit(page['parentId'], page['taskId'], task_no, score)
            continue

    def login(self, username, password):

        password = made_md5(made_md5(password) + "fa&s*l%$k!fq$k!ld@fjlk")
        data = {
            'username': username,
            'password': password,
            'ut': get_ut(username + password, 22)
        }

        response = self.session.post('https://sso.ismartlearning.cn/v2/tickets-v2', data=data).json()
        if response['result']['code'] == -27:
            print(response['result']['msg'])
            return None
        self.uid = response['data']['uid']
        return response

    def buy_book(self):
        headers = {
            'User-Agent': 'Android-Ismart-Moblie 2.5.3',
            'clientId': '1a699fb4d1a88c29',
            'X-Requested-With': 'android',
            'XOT': '1.4.0',
            'Host': 'book-api.ismartlearning.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }

        params = (
            ('ticket', self.service_ticket('https://book-api.ismartlearning.cn/client/books/buy-book')),
        )

        response = requests.get('https://book-api.ismartlearning.cn/client/books/buy-book', headers=headers,
                                params=params)

        ret = []
        for i in response.json()['data']:
            ret.insert(0, {
                "bookName": i['bookName'],
                "bookId": i['bookId'],
            })
        return ret

    def tree(self):
        headers = {
            'User-Agent': 'Android-Ismart-Moblie 2.5.3',
            'uid': str(self.uid),
            'X-Requested-With': 'android',
            'XOT': '1.4.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '50',
            'Host': 'book-api.ismartlearning.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }

        data = {
            'bookId': self.book_id,
            'bookType': '1'
        }

        url = 'https://book-api.ismartlearning.cn/client/books/tree'

        params = {'ticket': self.service_ticket(url)}

        response = self.session.post(url, headers=headers, params=params, data=data)

        pages = response.json()['data']['pages']

        rest = response.json()['data']['chapters']
        name_list = []

        for i in rest:
            if 'UNIT' in i['name'] or 'Unit' in i['name']:
                id_list = []
                for a in rest:
                    if i['id'] == a['parentId']:
                        id_list.append({'Id': a['id']})
                name_list.insert(0, {
                    "bookName": i['name'],
                    "bookId": i['id'],
                    "page": id_list
                })
        return name_list[::-1], pages

    def service_ticket(self, url):
        headers = {
            'Host': 'sso.ismartlearning.cn',
            'user-agent': 'Android-Ismart-Moblie 2.5.3',
            'uid': str(self.uid),
            'x-requested-with': 'android',
            'xot': '1.4.0',
            'content-type': 'application/x-www-form-urlencoded',
            'content-length': '82',
            'accept-encoding': 'gzip',
        }
        response = self.session.post('https://sso.ismartlearning.cn/v1/serviceTicket', headers=headers,
                                     data={'service': url})

        return response.json()['data']['serverTicket']

    def submit(self, parent_id, task_id, task_no, score):
        headers = {
            'User-Agent': 'Android-Ismart-Moblie 2.5.3',
            # 'uid': '1570807', 暂时不需要

            'X-Requested-With': 'android',
            'XOT': '1.4.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '2794',
            'Host': 'study-api.ismartlearning.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }

        tasks_json = json.dumps([{
            "bookId": self.book_id,
            "chapterId": parent_id,
            "extendParams": {},
            "percent": 100,
            "qstJson": [{}],
            "result": '',
            "score": score,
            "seconds": random.randint(90, 120),
            "studyDate": int(time.time()) * 1000,
            "taskId": task_id,
            "taskNo": task_no,
            "uid": self.uid
        }])

        data = {
            'tasksJson': tasks_json,
            'ut': get_ut(tasks_json, 11)
        }
        url = 'https://study-api.ismartlearning.cn/client/task/score/submit'
        params = {'ticket': self.service_ticket(url)}

        response = self.session.post(url, headers=headers, params=params, data=data)

        print(response.text)


if __name__ == '__main__':
    # username = input("\n请输入您的用户名(手机号):")
    # password = input("请输入您的密码:")
    username = '17856189481'
    password = '251623126j'
    Login(username, password)
