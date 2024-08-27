import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading


def login_test(start, end, ip, delay_ms, rest, secret):
    while True:
        # 将延迟从毫秒转换为秒
        delay_s = delay_ms / 1000.0

        for num in range(start, end + 1):
            login_num = f"{num:04d}"
            login_name = f"VCA{login_num}"
            token_url = f"http://{ip}:81/seeyon/rest/token/{rest}/{secret}?loginName={login_name}&userAgentFrom=pc"

            try:
                response = requests.get(token_url)
                response.raise_for_status()

                data = response.json()

                if 'id' in data:
                    token = data['id']
                    print(f"{login_name} 登录成功, ID: {token}")
                    main_page_url = f"http://{ip}:81/seeyon/main.do?token={token}"
                    # 使用Selenium初始化Edge浏览器
                    driver = webdriver.Edge()
                    try:
                        # 使用token打开主页
                        driver.get(main_page_url)
                        # 等待主页加载（根据页面结构调整条件）
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.ID, 'wrapper'))
                        )
                        # OA 统计在线人数大概要7-8秒时间
                        time.sleep(8)
                        print(f"{login_name} 使用token {token} 访问了主页")
                    finally:
                        # 关闭浏览器
                        driver.quit()
                else:
                    print(f"{login_name} 登录失败")

            except Exception as e:
                print(f"{login_name} 请求失败: {e}")
            # 在请求之间添加延迟
            time.sleep(delay_s)


def run_in_threads(start, end, ip, delay_ms, num_threads, rest, secret):
    threads = []
    range_size = (end - start + 1) // num_threads
    for i in range(num_threads):
        range_start = start + i * range_size
        # 确保最后一个线程覆盖剩余范围
        range_end = start + (i + 1) * range_size - 1 if i != num_threads - 1 else end
        thread = threading.Thread(target=login_test, args=(range_start, range_end, ip, delay_ms, rest, secret))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# OA压力测试
if __name__ == "__main__":
    ip = '172.21.13.17'
    start = int(input("请输入开始范围（例如：1）: "))
    end = int(input("请输入结束范围（例如：100）: "))
    delay_ms = 1
    num_threads = int(input("请输入线程数（例如：2）: "))
    rest = 'ssoTest'
    secret = '26a608a5-2fcd-47be-8ff8-b2d14111ccad'

    run_in_threads(start, end, ip, delay_ms, num_threads, rest, secret)
