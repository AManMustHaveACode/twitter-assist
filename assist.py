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
from multiprocessing.dummy import Pool

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



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
        wait = WebDriverWait(self.browser, 3)
        check_wait = WebDriverWait(self.browser, 1)

        retries = 1
        is_follow = False
        print("try to follow url: %s" % url)

        while retries <= max_retries:
            print("now follow try is : %s" % retries)
            try:
                follow = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='primaryColumn']//div[@data-testid='placementTracking']//span[text()='关注' or text()='Follow']/ancestor::div[@role='button']")))  # 注意中英文  关注-- follow  
                follow.click()
                print("click the follow button")
                time.sleep(random.random())
                print(self.browser.current_url)
            except Exception as Error:
                # //div[@data-testid='primaryColumn']//div[@data-testid='placementTracking']//div[@role='button']//span[text()='正在关注']"  # 没有关注的按钮，但是有正在关注，成功
                print("follow click failed: %s, check if already following " % Error)
                try:
                    check_follow = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//div[@data-testid='placementTracking']//span[text()='正在关注' or text()='Following']")))  # unfollow  [contains(text(),'正在关注') or contains(text(), 'Unfollow')]
                    print("check follow result: %s" % check_follow)
                    print("already follow")
                    is_follow =True
                    break
                except TimeoutException as Error:
                    print("in follow timeout exception")
                    retries += 1
                    time.sleep(random.random())
                    print(Error)
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
                except TimeoutException as Error:
                    print("check follow timeout")
                    retries += 1
                    self.browser.refresh()
                    # return_str += "follow failed, can't get unfollow"
        if not is_follow:
            return_str += "follow failed, can't get unfollow"
        print(" follow return str is : %s" % return_str)
        return is_follow, return_str
    
    
    def like_retweet_and_reply(self, url, max_retries, reply_text="真不错！！！"):
        print("in like retweet and reply")
        self.browser.get(url)
        now_handle = self.browser.current_window_handle
        self.browser.switch_to.window(now_handle)
        wait = WebDriverWait(self.browser, 5)
        check_wait = WebDriverWait(self.browser, 2)
        
        return_str = ""

        like_succ = False
        retries = 1
        print("before while")
        while retries <= max_retries:
            print("now like try is : %s" % retries)
            try:
                like = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@data-testid='primaryColumn']//article[@data-testid='tweet'])[1]//div[@data-testid='%s']" % "like")))
                like.click()
                time.sleep(random.random())
                # time.sleep(1 * random.randrange(1,3))
                
            except Exception as Error:
                try:
                    check_follow = check_wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@data-testid='primaryColumn']//article[@data-testid='tweet'])[1]//div[@data-testid='%s']" % "unlike")))  # unfollow  [contains(text(),'正在关注') or contains(text(), 'Unfollow')]
                    print("check like result: %s" % check_follow)
                    print("already like")
                    like_succ = True
                    break
                except TimeoutException as Error:
                    retries += 1
                    time.sleep(random.random())
                    print(Error)
                    self.browser.refresh()
                    continue
        
            # check like succ
            if not like_succ:
                print("check like succ")
                try:
                    check = check_wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@data-testid='primaryColumn']//article[@data-testid='tweet'])[1]//div[@data-testid='%s']" % "unlike")))
                    print("like check succ")
                    like_succ = True
                    break
                except TimeoutException as Error:
                    print(Error)
                    retries += 1
                    time.sleep(random.random())
                    self.browser.refresh()

                    # return_str += "like failed, can't get unfollow button, the url is : %s " % url
                    # self.browser.close()
        if not like_succ:
            return_str += "like failed, can't get unlike button, the url is : %s " % url
            return like_succ, return_str
        

        print("like succ ")
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
                time.sleep(random.random())
            except Exception as error:
                try:
                    unretweet = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//article[@data-testid='tweet']//div[@data-testid='unretweet']")))
                    print('retweet succ')
                    retweet_succ = True
                    break
                except Exception as Error:
                    print(Error)
                    retries += 1
                    self.browser.refresh()
                    continue
            if not retweet_succ:
                try:
                    unretweet = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//article[@data-testid='tweet']//div[@data-testid='unretweet']")))
                    print('retweet succ')
                    retweet_succ = True
                    break
                except Exception as Error:
                    print(Error)
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
                print("reply succ")

            except Exception as Error:
                print(Error)
                retries += 1
                self.browser.refresh()
                continue

            # check reply succ
            try:
                print("Check is reply text: %s  ,,,,,, in span " % reply_0)
                check_reply = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//div[@data-testid='cellInnerDiv']//article[@data-testid='tweet']//span[contains(text(), '%s')]" % reply_0)))
                print("reply check succ")
                reply_succ = True
                break
            except Exception as Error:
                print(Error)
                retries += 1
                time.sleep(random.random())
                self.browser.refresh()
                continue
                        
        if not reply_succ:
            return_str += "reply can't check status, the url is : %s " % url
            return reply_succ, return_str
        else:
            return reply_succ, "reply task succ!!!!!!!!!!"
        #     try:
        #         print("Check is reply text: %s ,,,,,, in span " % reply_0)
        #         print("check reply text: %s in span " % reply_0)
        #         check_reply = check_wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']//div[@data-testid='cellInnerDiv']//article[@data-testid='tweet']//span[contains(text(), '%s')]" % reply_0)))
        #         print("outter reply check succ!!!!!!!")
        #     except Exception as Error:
        #         print(Error)
        #         print("check reply timeout, Failed!")
        #         reply_succ = False
        #         return_str += "reply can't check status, the url is : %s " % url
        
        # return reply_succ, return_str
        
    def close(self):
        self.browser.close()
        


class TwitterWorker():
    twitter_url = "https://twitter.com/"
    ads_url = "http://local.adspower.net:50325"
    # ads_url = "http://127.0.0.1:50325"
    start_url = "/api/v1/browser/start?user_id=%s"
    close_url = "/api/v1/browser/stop?user_id=%s"

    def __init__(self):
        if sys.platform.startswith("win"):
            print(os.path.realpath(__file__))
            print(os.getcwd())
            config = os.path.join(os.getcwd(), "config.yaml")
            print(config)
        else:
            config = "./config.yaml"
        try:
            with open(config, encoding='utf-8') as yml:
                config_yaml = yaml.load(yml, Loader=yaml.BaseLoader)
                process_num = int(config_yaml["max_process"])
                dingding_token = config_yaml["dingding_token"]
                sleep_time = int(config_yaml["sleep_time"])
                max_retry_times =  int(config_yaml["max_retry_times"])
        except Exception as Error:
            print(Error)
            print("load config failed, please check!!!")
            time.sleep(200)
            sys.exit(2)
            

        self.process_num = process_num if process_num > 0 else 1
        self.dingding_token = dingding_token
        dingutil = DingdingUtils(self.dingding_token)
        self.dingutil = dingutil
        self.sleep_time = sleep_time
        self.max_retry_times = max_retry_times
        
        self.all_tags = self.get_tag_user_msg()

        self.all_reply = self.get_all_reply()

        self.ads_account_dict = self.get_accounts()

    
    def get_accounts(self):
        ads_account_dict = {}
        if sys.platform.startswith("win"):
            #reply_dir = ".\\accounts.txt"
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
                except Exception as Error:
                    print(Error)
                    print("accounts.txt config error, please check")
                    time.sleep(100)
                    sys.exit(3)
                    
        return  ads_account_dict
    
    def split_task_and_run(self):
        # 设置的进程数，每个进程均分task
        worker_pool = Pool(processes=self.process_num)
        # all_files = os.listdir("./tasks")
        print("in split tasks")
        ads_account_list = list(self.ads_account_dict.keys())
        print(ads_account_list)

        user_num_for_process = len(ads_account_list) // self.process_num
        print("per task num: %s" % user_num_for_process)
        print("process num: %s" % self.process_num)

        for i in range(self.process_num + 1):  
            process_users = ads_account_list[i * user_num_for_process: (i+1) * user_num_for_process]
            print("got users list: %s" % process_users)
            print(type(process_users))
            if not process_users:
                print("in continue")
                continue
            worker_pool.apply_async(self.exec_task, args=(process_users,), callback=self.call_back_results, error_callback=self.error_call_backs)
            print("added !!!!!")
            time.sleep(5)
            
        
        worker_pool.close()
        worker_pool.join()

    def exec_task(self, process_users):
        print('in exec task')
        error_str = ""
        succ_count = 0
        failed_count = 0
        # ads_account_list = list(self.ads_account_dict.keys())
        # process_users = ads_account_list[ads_user_index: ads_user_index + ads_users_num]
        
        for ads_user in process_users:
            print("now ads User is: %s" % ads_user)
            try:
                time.sleep(random.random())
                twitter_bot = self.ads_twitter_helper(ads_user)
            except Exception as error:
                error_str += "ads_user: %s, bad happends" % ads_user 
                return error_str
            if sys.platform.startswith("win"):
                task_dir = os.path.join(os.getcwd(), "tasks")
            else:
                task_dir = "./tasks"
            all_files = os.listdir(task_dir)
            for file_name in all_files:
                single_str = "ads_user's task has follow error, ads_user: %s follow_user: %s  , failed "
                if os.path.splitext(file_name)[1] != '.yaml':
                    continue
                with open(os.path.join(task_dir, file_name), encoding="utf-8") as yml:
                    yaml_data = yaml.load(yml, Loader=yaml.BaseLoader)
                    retweet_url = yaml_data["url"]
                    follow_users = yaml_data["to_follow"]
                follow_error = ""
                for follow_user in follow_users:
                    twitter_user_url = self.twitter_url + follow_user
                    try:
                        res, msg = twitter_bot.follow(twitter_user_url, self.max_retry_times)
                    except Exception as Error:
                        print(Error)
                        failed_count += 1
                        follow_error += single_str % (ads_user, follow_user) + "\n"
                        continue
                    if not res:
                        follow_error += single_str % (ads_user, follow_user) + "for the reason of : %s" % msg + "\n"
                    
                    time.sleep(random.randint(1, self.sleep_time))
                if follow_error:
                    # 存在follow error，所以跳过后续；like和retweet也是必须都成功才算是完成一个任务
                    failed_count += 1
                    error_str += follow_error + "\n"
                    continue
                     
                # retweet
                single_retweet_str = "ads_user's task: %s has retweet error, ads_user: %s reweet_url: %s  , failed "
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
                    succ, msg = twitter_bot.like_retweet_and_reply(retweet_url, self.max_retry_times, retweet_msg)
                except Exception as Error:
                    print(Error)
                    failed_count += 1
                    error_str += single_retweet_str % (file_name, ads_user, retweet_url) + ": exception" + "\n"
                    continue
                    
                if not succ:
                    failed_count += 1
                    error_str += single_retweet_str % (file_name, ads_user, retweet_url) + ": " + msg + "\n"
                    continue


                succ_count += 1
                time.sleep(random.randint(1, self.sleep_time))

            twitter_bot.close()
            self.ads_closer(ads_user)

        
        if not error_str:
            return str(succ_count)
        return error_str
        

    def call_back_results(self, result):
        print("in callback")
        print("*****************************")
        print(result)
        print(type(result))
        

        if result.isdigit():
            # all succ
            self.dingutil.send_dingding_msg("Twitter assist: this task all succ, succ count is %s " % str(result))
        else:
            # has succ , althrough error exists,
            self.dingutil.send_dingding_msg("Twitter assist has error: " + result)
            
        # check if need to send dingding
        print("*****************************")
        print("in callback end")
        
    def error_call_backs(self, result):
        print("*****************************")
        print("in error call back")
        self.dingutil.send_dingding_msg("Twitter assist: this task some thing went wrong: %s" % str(result))
        print(result)
        print("*****************************")
        

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
        except Exception as Error:
            print(Error)
            time.sleep(200)
            sys.exit(1)
        print(all_tags)
        return all_tags
        # random_tags = random.choices(all_tags, k=count)
        # print("users to tag %s" % random_tags)
        # return "\n ".join(random_tags) + "\n"

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
        except Exception as Error:
            print(Error)
            time.sleep(200)
            sys.exit(1)
        return all_reply
        # return all_reply[random.randint(0, len(all_reply) - 1)] + "\n" if len(all_reply) > 0 else ""
        
    def ads_twitter_helper(self, ads_user="j26fqfi"):
        print("now is user:%s" % ads_user)
        retries = 0
        while retries <= self.max_retry_times:
            print("ads start try: %s " % retries)
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
                    time.sleep(2 * random.randrange(1, self.sleep_time))
                    continue
                webdriver_location = resp["data"].get("webdriver")
                selenium_server = resp["data"]["ws"]["selenium"]
                print(webdriver_location)
                tb = TwitterClickBot(webdriver_location, selenium_server)
                return tb
            except Exception as Error:
                print(Error)
                retries += 1
                print("ads start failed, wait to retry")
                time.sleep(2 * random.randrange(1, self.sleep_time))
                
        raise Exception("ads start error,  please check!")   
        
    
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
        except Exception as Error:
            print(Error)
            print("something went wrong, please close ads manually!!!! ")
            time.sleep(200)
            sys.exit(1)
            

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
                print("Ding Msg Send Error, got : %s" % data.get("errmsg"))
        except Exception as Error:
            print("Ding Msg Send Error, got : %s" % Error)

if __name__ == "__main__":
    final_day = datetime.strptime("2022-06-02", "%Y-%m-%d")
    now_day = datetime.now()
    if now_day > final_day:
        print("The trial period for this product has expired, existing......")
        time.sleep(500)
        sys.exit(1)
        
    else:
        try:
            tw = TwitterWorker()
            tw.split_task_and_run()
        except Exception as Error:
            print(Error)
            time.sleep(200)
            

    time.sleep(500)
    # resp = requests.get(ads_url + start_url).json()
    # if resp["code"] != 0:
    #     print(resp["msg"])
    #     print("please check ads_id")
    #     sys.exit(1)
    # webdriver_location = resp["data"].get("webdriver")
    # selenium_server = resp["data"]["ws"]["selenium"]
    # # webdriver_location = "/Users/wyw/Library/Application Support/adspower_global/cwd_global/source/webdriver_99/chromedriver.app/Contents/MacOS/chromedriver"
    # print(webdriver_location)

    # tb = TwitterClickBot(webdriver_location, selenium_server)
    # # tb.follow()
    # tweet_test_url = "https://twitter.com/espn/status/1523299787239424000"
    # tb.retweet_and_reply(tweet_test_url)
    # time.sleep(1000)
