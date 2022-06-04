# -*- coding:utf-8 -*-
import time
import sys
import os
import requests
import random
import yaml
from datetime import datetime
# import multiprocessing
# from multiprocessing import Pool
# from multiprocessing.dummy import Pool  # no mulit process anymore

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 按照task分，每个用户都跑一个task；所有的用户跑完一个task再跑下一个
class TwitterClickBot():
    def __init__(self, driver_location, selenium_server):
        print(driver_location)
        print(selenium_server)
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", selenium_server)
        self.browser = webdriver.Chrome(driver_location, options=chrome_options)
    
    
    def follow(self, url, max_retries=1):
        return_str = ""
        self.browser.get(url)
        now_handle = self.browser.current_window_handle
        self.browser.switch_to.window(now_handle)
        wait = WebDriverWait(self.browser, 5)
        check_wait = WebDriverWait(self.browser, 3)

        retries = 1
        is_follow = False
        print("try to follow url: %s" % url)

        while retries <= max_retries:
            print("now follow try is : %s" % retries)
            try:
                follow = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='primaryColumn']//div[@data-testid='placementTracking']//span[text()='关注' or text()='Follow']/ancestor::div[@role='button']")))  # 注意中英文  关注-- follow  
                follow.click()
                print("click the follow button")
                time.sleep(1 * random.randrange(1,3))
                print(self.browser.current_url)
            except Exception as error:
                # //div[@data-testid='primaryColumn']//div[@data-testid='placementTracking']//div[@role='button']//span[text()='正在关注']"  # 没有关注的按钮，但是有正在关注，成功
                print("follow click failed, check if already following ")
                try:
                    check_follow = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//div[@data-testid='placementTracking']//span[text()='正在关注' or text()='Following']")))  # unfollow  [contains(text(),'正在关注') or contains(text(), 'Unfollow')]
                    print("check follow result: %s" % check_follow)
                    print("already follow!!!!!!!!!!!!!!")
                    is_follow =True
                    break
                except TimeoutException as error:
                    print("in follow timeout exception")
                    retries += 1
                    time.sleep(2 * random.random())
                    # print(error)
                    self.browser.refresh()
                    continue
                # retries += 1
                # self.browser.refresh()
                # print("follow action timeout error")

                        
            if not is_follow:
                try:
                    check_follow = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//div[@data-testid='placementTracking']//span[text()='正在关注' or text()='Following']")))  # unfollow
                    print("check follow result outter: %s" % check_follow)
                    is_follow = True
                    break
                except TimeoutException as error:
                    print("check follow timeout")
                    retries += 1
                    self.browser.refresh()
                    # return_str += "follow failed, can't get unfollow"
        if not is_follow:
            return_str += "follow failed, can't get unfollow button"
        return_str = return_str or "follow succ!!!!!!!!!!"
        print(" follow return str is : %s" % return_str)
        return is_follow, return_str
    
    
    def like_retweet_and_reply(self, url, max_retries, reply_text="真不错！！！"):
        print("in like retweet and reply")
        self.browser.get(url)
        now_handle = self.browser.current_window_handle
        self.browser.switch_to.window(now_handle)
        wait = WebDriverWait(self.browser, 5)
        check_wait = WebDriverWait(self.browser, 3)
        
        return_str = ""

        like_succ = False
        retries = 1
        print("before while")
        while retries <= max_retries:
            print("now like try is : %s" % retries)
            try:
                like = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@data-testid='primaryColumn']//article[@data-testid='tweet'])[1]//div[@data-testid='%s']" % "like")))
                like.click()
                # time.sleep(random.random())
                time.sleep(1 * random.randrange(1,3))
                
                
            except Exception as error:
                try:
                    check_follow = check_wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@data-testid='primaryColumn']//article[@data-testid='tweet'])[1]//div[@data-testid='%s']" % "unlike")))  # unfollow  [contains(text(),'正在关注') or contains(text(), 'Unfollow')]
                    print("check like result: %s" % check_follow)
                    print("already like")
                    like_succ = True
                    break
                except TimeoutException as error:
                    retries += 1
                    time.sleep(random.random())
                    print(error)
                    self.browser.refresh()
                    continue
        
            # check like succ
            if not like_succ:
                print("check like succ")
                try:
                    check = check_wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@data-testid='primaryColumn']//article[@data-testid='tweet'])[1]//div[@data-testid='%s']" % "unlike")))
                    print("like check succ")
                    like_succ = True
                    time.sleep(1 * random.randrange(1,3))
                    break
                except TimeoutException as error:
                    print(error)
                    retries += 1
                    time.sleep(random.random())
                    self.browser.refresh()
                    # return_str += "like failed, can't get unfollow button, the url is : %s " % url
                    # self.browser.close()
        if not like_succ:
            return_str += "like failed, can't get unlike button, the url is : %s " % url
            return like_succ, return_str
        

        print("like succ !!!!!!!!!!!")
        time.sleep(random.random())

        retries = 1
        retweet_succ = False

        while retries <= max_retries:
            print("now reweet try is : %s" % retries)
            try:
                retweet = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@data-testid='primaryColumn']//article[@data-testid='tweet'])[1]//div[@data-testid='%s']" % "retweet")))  # 注意中英文  关注 -- follow
                retweet.click()
                time.sleep(random.random())
                # time.sleep(1 * random.randrange(1,3))
                
                menu = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@data-testid='retweetConfirm'])")))
                menu.click()
                print('点击reweet按钮')
                time.sleep(1 * random.randrange(1,3))
                # time.sleep(random.random())
            except Exception as error:
                try:
                    unretweet = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//article[@data-testid='tweet']//div[@data-testid='unretweet']")))
                    print('retweet succ!!!!!!!')
                    retweet_succ = True
                    break
                except Exception as error:
                    print(error)
                    retries += 1
                    self.browser.refresh()
                    continue
            if not retweet_succ:
                try:
                    unretweet = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//article[@data-testid='tweet']//div[@data-testid='unretweet']")))
                    print('retweet succ!!!!!!!!!')
                    retweet_succ = True
                    break
                except Exception as error:
                    print(error)
                    time.sleep(1 * random.randrange(1,3))
                    retries += 1
                    self.browser.refresh()
                
        if not retweet_succ:
            return_str += "retweet failed, can't get retweet button, the url is : %s " % url
            return retweet_succ, return_str
            
        retries = 1
        reply_succ = False
        reply_0 = reply_text.split(" \n")[0].strip()

        while retries <= max_retries:
            #  replies
            print("now reply try is : %s" % retries)
            try:
                print("input")
                input = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//div[@class='DraftEditor-root']//div[@data-contents='true']")))
                input.send_keys(reply_text)
                
                print("click reply")
                reply = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@data-testid='primaryColumn']//div[@data-testid='tweetButtonInline' and @role='button'])[1]")))
                print(reply)
                reply.click()
                time.sleep(1 * random.randrange(1,3))
            except Exception as error:
                print(error)
                retries += 1
                self.browser.refresh()
                continue

            # check reply succ
            try:
                print("Check is reply text: %s  ,,,,,, in span " % reply_0)
                check_reply = check_wait.until(EC.presence_of_element_located((By.XPATH, '''//div[@data-testid='primaryColumn']//div[@data-testid='cellInnerDiv']//article[@data-testid='tweet']//span[contains(text(), "%s")]''' % reply_0)))
                print("reply check succ!!!!!!!!!")
                reply_succ = True
                break
            except Exception as error:
                print(error)
                retries += 1
                time.sleep(random.random())
                self.browser.refresh()
                continue
                        
        if not reply_succ:
            return_str += "reply can't check status, the url is : %s " % url
            return reply_succ, return_str
        else:
            return reply_succ, "reply task succ!!!!!!!!!!"
        
    def close(self):
        self.browser.close()
        

class DingdingUtils:

    def __init__(self, token):
        self.token = token
        self.dingUrl = "https://oapi.dingtalk.com/robot/send?access_token=%s" % token
        
    def send_dingding_msg(self, msg):
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        data = {
            "msgtype": "text",
            "text": {
                "content": msg
            }
        }

        try:
            res = requests.post(self.dingUrl, json=data, headers=header, timeout=5)
            data = res.json()
            if data.get("errcode") != 0:
                print("Ding Msg Send error, got : %s" % data.get("errmsg"))
        except Exception as error:
            print("Ding Msg Send error, got : %s" % error)

# has active api; no need  数据库名固定位ads_info  每次执行ads的打开操作，执行update sqlite 保证每个ads user id只保存一个端口

# class SqlUtils():

#     create_db_sql = """
#     create table ads (id int primary key not null,
#     user_id char(20),
#     port int not null,
#     ct datetime
#     );
#     """

#     def __init__(self, db_name="ads_info") -> None:
#         conn = sqlite3.connect(db_name)
#         cur = conn.cursor()
#         self.cursor = cur

#     def ct_db(self):
#         self.cursor.execute(self.create_db_sql)
        

#     def insert():
#         pass

#     def update(self, ads_id):
#         # 按照ads_id 插入或更新
#         pass
    
class AdsHelper():
    ads_url = "http://local.adspower.net:50325"
    start_url = "/api/v1/browser/start?user_id=%s"
    close_url = "/api/v1/browser/stop?user_id=%s"
    active_url = "/api/v1/browser/active?user_id=%s"  # 判断对应的浏览器是否已经打开
    max_retries = 3
    sleep = 3

    def ads_twitter_helper(self, ads_user="j26fqfi"):
        print("In ads start action, now is user:%s" % ads_user)
        active, data = self.is_active(ads_user)
        print(active)
        print(data)
        if active:
            print("ads browser active already! ")
            webdriver_location = data.get("webdriver")
            selenium_server = data.get("ws", {}).get("selenium")
            tb = TwitterClickBot(webdriver_location, selenium_server)
            return tb

        retries = 0  # no active, open a new one
        while retries <= self.max_retries:
            print("ads start try count: %s " % retries)
            try:
                url = self.ads_url + self.start_url % ads_user
                print(url)
                session = requests.Session()
                session.trust_env = False
                res = session.get(url)
                print("ads log ***********************")
                print(res)
                print(res.content)
                resp = res.json()
                print(resp)
                print("*****************************")
                if resp["code"] != 0:
                    print("ads interface resp msg: %s" % resp["msg"])
                    print("please check ads_id")
                    retries += 1
                    time.sleep(1 * random.randrange(1, self.sleep))
                    continue
                webdriver_location = resp["data"].get("webdriver")
                selenium_server = resp["data"]["ws"]["selenium"]
                print(webdriver_location)
                tb = TwitterClickBot(webdriver_location, selenium_server)
                return tb
            except Exception as error:
                print(error)
                retries += 1
                print("ads start failed, wait to retry")
                time.sleep(1 * random.randrange(1, self.sleep))
        print("ads user: %s has start error,  please check!!!!!!!!" % ads_user) 
        return False
        

    def ads_closer(self, ads_user):
        print("user:%s is closing" % ads_user)
        try:
            url = self.ads_url + self.close_url % ads_user
            print(url)
            session = requests.Session()
            session.trust_env = False
            res = session.get(url)
            resp = res.json()
            if resp["code"] != 0:
                print("ads closing resp msg: %s" % resp["msg"])
        except Exception as error:
            print(error)
            print("something went wrong, please close ads manually!!!! ")
            time.sleep(200)
            sys.exit(1)

    def is_active(self, ads_user):
        print("in active judge ***********")
        retries = 0
        while retries <= self.max_retries:
            print("ads active start try count: %s " % retries)
            try:
                url = self.ads_url + self.active_url % ads_user
                print(url)
                session = requests.Session()
                session.trust_env = False
                res = session.get(url)
                resp = res.json()
                print(resp)
                if resp["code"] != 0:
                    print("ads active resp msg: %s" % resp["msg"])
                    time.sleep(2 * random.randrange(1, self.sleep))
                    retries += 1
                    continue
                status = resp['data'].get('status')
                if status == "Active":
                    print("browser is open already, get info")
                    return True, resp['data']
                return False, {}
            except Exception as error:
                print(error)
                print("something went wrong, can't get ads active, try in next time !!!! ")
                time.sleep(2 * random.randrange(1, self.sleep_time))
                retries += 1

        return False, {}
        # {
        #     "code":0,
        #     "data":{
        #         "status": "active",   // 浏览器已打开运行中 "active" ，未打开则是 "inactive"
        #         "ws":{
        #         "selenium":"127.0.0.1:xxxx",    //浏览器debug接口，可用于selenium自动化
        #         "puppeteer":"ws://127.0.0.1:xxxx/devtools/browser/xxxxxx"   //浏览器debug接口，可用于puppeteer自动化
        #         }
        #     },
        #     "msg":"success"
        #     }

        #     //执行失败
        #     {
        #     "code":-1,
        #     "data":{},
        #     "msg":"failed"
        # }
        ...


class ConfigUtils():
    
    @staticmethod
    def get_tag_user_msg():
        all_tags = []
        if sys.platform.startswith("win"):
            #reply_dir = ".\\tag_users.txt"
            reply_dir = os.path.join(os.getcwd(), "tag_users.txt")
            print(reply_dir)
        else:
            reply_dir = "./tag_users.txt"
        try:
            
            with open(reply_dir, encoding='utf-8') as tags:
                while True:
                    line = tags.readline()
                    if line.startswith("#"):
                        continue
                    
                    if not line or line == "\n":
                        break
                    all_tags.append("@" + line.strip())
        except Exception as error:
            print(error)
            time.sleep(200)
            sys.exit(1)
        print(all_tags)
        return all_tags

    @staticmethod
    def get_all_reply():
        all_reply = []
        if sys.platform.startswith("win"):
            reply_dir = os.path.join(os.getcwd(), "reply.txt")
            print(reply_dir)
        else:
            reply_dir = "./reply.txt"
        try:
            with open(reply_dir, encoding='utf-8') as reply:
                while True:
                    line = reply.readline()
                    if line.startswith("#"):
                        continue
                    
                    if not line or line == "\n":
                        break
                    all_reply.append(line)
        except Exception as error:
            print(error)
            print("reply config error, please check!!!!!!")
            time.sleep(200)
            sys.exit(1)
        return all_reply
    
    @staticmethod
    def get_accounts():
        ads_account_dict = {}
        if sys.platform.startswith("win"):
            reply_dir = os.path.join(os.getcwd(), "accounts.txt")
            print(reply_dir)
        else:
            reply_dir = "./accounts.txt"
        with open(reply_dir, encoding='utf-8') as all_accounts:
            while True:
                line = all_accounts.readline()
                if line.startswith("#"):
                    continue
                
                if not line or line == "\n":
                    print("read complete")
                    break
                line = line.strip()
                try:
                    line_splits = line.split("---")
                    print(type(line_splits))
                    print(type(line_splits[0]))
                    ads_account_dict.update({line_splits[0]: [line_splits[1], line_splits[2], line_splits[3]]})
                except Exception as error:
                    print(error)
                    print("accounts.txt config error, please check!!!!!!")
                    time.sleep(100)
                    sys.exit(3)
                    
        return  ads_account_dict

    @staticmethod
    def get_config():
        if sys.platform.startswith("win"):
            print(os.path.realpath(__file__))
            print(os.getcwd())
            config = os.path.join(os.getcwd(), "config.yaml")
            print(config)
        else:
            config = "./config.yaml"
        data = {}
        try:
            with open(config, encoding='utf-8') as yml:
                config_yaml = yaml.load(yml, Loader=yaml.BaseLoader)
                dingding_token = config_yaml["dingding_token"]
                sleep_time = int(config_yaml["sleep_time"])
                max_retry_times =  int(config_yaml["max_retry_times"])
                data.update({"dingding_token": dingding_token, "sleep_time": sleep_time, "max_retry_times": max_retry_times})
        except Exception as error:
            print(error)
            print("load config failed, please check!!!")
            time.sleep(200)
            sys.exit(2)
        return data
        


class MainExecTask():
    twitter_url = "https://twitter.com/"

    def __init__(self) -> None:
        cu = ConfigUtils()
        accounts = cu.get_accounts()
        self.accounts = accounts
        all_reply = cu.get_all_reply()
        self.all_reply = all_reply
        ads_account_dict = cu.get_accounts()
        self.ads_account_dict = ads_account_dict
        config_data = cu.get_config()
        self.config_data = config_data
        self.all_tags = cu.get_tag_user_msg()

        adshelper = AdsHelper()
        self.adshelper = adshelper


    def exec_task(self):
        # get all accounts
        all_ads_users = self.accounts.keys()

        # get tasks
        if sys.platform.startswith("win"):
            task_dir = os.path.join(os.getcwd(), "tasks")
        else:
            task_dir = "./tasks"
        all_files = os.listdir(task_dir)
        print("all tasks files: %s" % all_files)

        max_retry_times = self.config_data.get("max_retry_times")
        sleep_time = self.config_data.get("sleep_time")
        dingding_token = self.config_data.get("dingding_token")
        dingutil = DingdingUtils(dingding_token)

        all_tasks_error = ""  # 正确的
        all_tasks_str = ""    # 错误的

        for file_name in all_files:  # 所有用户做完一个task，再做下一个
            single_task_error = ""
            single_task_str = ""
            failed_count = 0
            succ_count = 0

            if os.path.splitext(file_name)[1] != '.yaml':
                continue
            try:
                with open(os.path.join(task_dir, file_name), encoding="utf-8") as yml:
                    yaml_data = yaml.load(yml, Loader=yaml.BaseLoader)
                    retweet_url = yaml_data["url"]
                    follow_users = yaml_data["to_follow"]
            except Exception as error:
                print(error)
                single_task_error += "task: %s has open error, check the encoding and task file's config;  " % file_name
                continue
            
            print("Now task name is : %s ~~~~~~~~~~" % file_name)
            try:
                for ads_user in all_ads_users:
                    print("Now user: %s is doing task: %s ~~~~~~~~" % (ads_user, file_name))
                    try:
                        twitter_bot = self.adshelper.ads_twitter_helper(ads_user)
                    except Exception as error:
                        print(error)
                        failed_count += 1
                        single_task_error += "ads user : %s got an ads start error, in task: %s;  " % (ads_user, file_name)
                        continue
                    if not twitter_bot:
                        failed_count += 1
                        single_task_error += "ads user : %s got an ads start error, in task: %s;  " % (ads_user, file_name)
                        continue

                    follow_succ = False
                    for follow_user in follow_users:
                        print("now following: %s" % follow_user)
                        twitter_user_url = self.twitter_url + follow_user
                        try:
                            res, msg = twitter_bot.follow(twitter_user_url, max_retry_times)
                        except Exception as error:
                            print(error)
                            single_task_error += "ads user : %s has follow failed, in task: %s, for the reason of: %s; " % (ads_user, file_name, error)
                            break
                        if not res:
                            single_task_error += "ads user : %s has follow failed, in task: %s, for the reason of: %s; " % (ads_user, file_name, msg)
                            break
                        follow_succ = True
                        time.sleep(random.randint(1, sleep_time))
                    
                    if not follow_succ:
                        failed_count += 1  # 一个follow失败，用户的这个task即视为失败，失败数加1
                        print("follow has error, exec next ads user")
                        continue

                    reply_info = yaml_data['reply']
                    print("reply info: %s" % reply_info)
                    tag_count = reply_info.get("tag_count")
                    need_email = reply_info.get('need_email')
                    need_token = reply_info.get('need_token')
                    need_dsid = reply_info.get('need_dsid')

                    retweet_msg = ""
                    print("all_reply: %s" % self.all_reply)
                    retweet_msg += self.all_reply[random.randint(0, len(self.all_reply) - 1)] + " \n" if len(self.all_reply) > 0 else ""
                    print("retweet msg: %s" % retweet_msg)
                    random_tags = random.sample(self.all_tags, k=int(tag_count))
                    retweet_msg += " \n".join(random_tags) + " \n"
                    ads_user_info = self.ads_account_dict.get(ads_user)
                    print("user_info: %s" % ads_user_info)
                    if need_email == "true" or need_email == True or need_email == "True":
                        retweet_msg += ads_user_info[0] + " \n"
                    if need_token == "true" or need_token == True or need_token == "True":
                        retweet_msg += ads_user_info[1] + " \n"
                    if need_dsid == "true" or need_dsid == True or need_dsid == "True":
                        retweet_msg += str(ads_user_info[2]) + " \n"
                    print("retweet msg is: %s" % retweet_msg)

                    try:
                        succ, msg = twitter_bot.like_retweet_and_reply(retweet_url, max_retry_times, retweet_msg)
                    except Exception as error:
                        print(error)
                        failed_count += 1
                        single_task_error += "ads user : %s has reweet failed, in task: %s, for the reason of: %s; " % (ads_user, file_name, error)
                        continue
                        
                    if not succ:
                        failed_count += 1
                        single_task_error += "ads user : %s has reweet failed, in task: %s, for the reason of: %s; " % (ads_user, file_name, msg)
                        continue

                    succ_count += 1
                    time.sleep(random.randint(1, sleep_time))
                    if len(twitter_bot.browser.window_handles) > 1:
                        twitter_bot.close()
            except Exception as error:
                print(error)
                failed_count += 1
                single_task_error += "ads users exec got unexpected error : %s, in task: %s; try next task " % (ads_user, file_name)
                continue

            single_task_str += "Twitter assist msg:\n  task: %s exec completed end, succ count is: %s ~~~~~~~~, failed count is: %s ~~~~~~~~~~\n" % (file_name, succ_count, failed_count)
            if single_task_error:
                single_task_str += "failed msg detail is : %s .....................\n" % single_task_error
            print("Task all user completed, all msg is: %s " % single_task_str)
            dingutil.send_dingding_msg(single_task_str)  # 一个task一个dingding  msg



if __name__ == "__main__":
    main_task = MainExecTask()
    main_task.exec_task()
    time.sleep(200)

    # TODO reply 检查的时候，xpath带引号的判断    

        






            
