#!/usr/bin/env python3
# -*- utf-8 -*-
# pip install -i https://testpypi.python.org/pypi selenium-page-objects


import time, os
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from page_objects import PageObject, PageElement, PageElements, PageWait

class LoginPage(PageObject):
    page_title = PageElement(xpath='/html/body/div/div/p')
    username = PageElement(name="UserName")
    password = PageElement(name="Password")
    submit = PageElement(xpath='//*[@id="form"]/div/div[3]/button')

class MainMenu(PageObject):
    page_title = PageElement(xpath='/html/body/nav/div/div[1]/span/b')
    login_username = PageElement(xpath='//*[@id="bs-example-navbar-collapse-1"]/div/a/span/b[2]')
    system_manage = PageElement(xpath='//*[@id="menu"]/li/div[1]')
    provider_info_manage = PageElement(xpath='//*[@id="menu"]/li/div[3]')
    service_manage = PageElement(xpath='//*[@id="menu"]/li/div[5]')
    order_manage = PageElement(xpath='//*[@id="menu"]/li/div[7]/span')
    order_approve = PageElement(xpath='//*[@id="business"]/a/span')
    member_manage = PageElement(xpath='//*[@id="menu"]/li/div[9]')
    data_statistics = PageElement(xpath='//*[@id="menu"]/li/div[11]')
    logout = PageElement(xpath='//*[@id="bs-example-navbar-collapse-1"]/div/ul/li[2]/a')
    logout_confirm = PageElement(xpath='//*[@id="LogOut"]/div/div/div[2]/div/button[1]')
    logout_cancel = PageElement(xpath='//*[@id="LogOut"]/div/div/div[2]/div/button[2]')

class OrderManage(PageObject):
    search_name = PageElement(id_='name')
    pass_order_all = PageElement(xpath='//*[@id="searchForm"]/div[5]/button[1]')
    refuse_order_all = PageElement(xpath='//*[@id="searchForm"]/div[5]/button[2]')
    order_list = PageElements(xpath='/html/body/div[1]/div[1]/table/tbody/tr')
    select_all = PageElement(xpath='/html/body/div[1]/div[1]/table/thead/tr/th[1]/div/label')
    modal = PageElement(xpath='//*[@id="DeleteModel"]')
    confirm_info = PageElement(xpath='//*[@id="DeleteModel"]/div/div/div[2]/p', timeout=30)
    pass_confirm = PageElement(xpath='//*[@id="DeleteModel"]/div/div/div[2]/div/button[1]')
    pass_concel = PageElement(xpath='//*[@id="DeleteModel"]/div/div/div[2]/div/button[2]')
    result_info = PageElement(xpath='//*[@id="MessageModel"]/div/div/div[2]/p', timeout=30)
    result_close = PageElement(xpath='//*[@id="MessageModel"]/div/div/div[2]/div/button')

    def get_order_list(self, elems):
        orders = []
        for elem in elems:
            order = []
            for i in range(2, 9):
                order.append(elem.find_element_by_xpath("td[{}]".format(i)).text)
            orders.append(order)
        return orders

def approve_orders(username, password, logger=None):
    driver = webdriver.Chrome()
    driver.maximize_window()
    is_pass = True
    try:
        current_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
        current_time1 = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        pic_path1 = os.path.dirname(os.getcwd()) + '\\report\\image\\' + current_time1 + '\\'
        if not os.path.exists(pic_path1):
            os.makedirs(pic_path1)
        pic_path = pic_path1 + current_time
        login = LoginPage(driver)
        login.get("http://192.168.2.247:15100/")
        login.username = username
        login.password = password
        login.submit.click()
        menu = MainMenu(driver)
        # 在订单审批页面循环批量审批订单
        for i in range(0, 200):
            logger and logger.info("Test times({})".format(i + 1))
            driver.refresh()
            menu.order_manage.click()
            menu.order_approve.click()
            sleep(1)
            driver.switch_to.frame("RIframe")
            order_manage = OrderManage(driver)
            orders = order_manage.order_list
            orders_list = order_manage.get_order_list(orders)
            logger and logger.info(orders_list)
            # 判断是否还有订单
            if orders_list:
                # 批量审批并且保持审批结果
                order_manage.select_all.click()
                order_manage.pass_order_all.click()
                driver.switch_to.default_content()
                logger and logger.info(order_manage.confirm_info.text)
                sleep(1)
                order_manage.pass_confirm.click()
                sleep(5)
                result_text = order_manage.result_info.text
                logger and logger.info(result_text)
                sleep(1)
                if '成功' not in result_text:
                    piture = pic_path + '_' + str(i) + '.png'
                    logger and logger.info(piture)
                    driver.save_screenshot(piture)
                    is_pass = False
                    driver.switch_to.default_content()
                    break
                order_manage.result_close.click()
                sleep(3)
                driver.switch_to.default_content()
            else:
                logger and logger.info("No orders.")
                driver.switch_to.default_content()
                is_pass = True
                break
        # 退出登录
        sleep(1)
        menu.login_username.click()
        menu.logout.click()
        menu.logout_confirm.click()
        sleep(1)
        return is_pass
    except Exception as e:
        logger and logger.error("Exception: " + str(e))
        return False
    finally:
        driver.quit()



if __name__ == '__main__':
    driver = webdriver.Firefox()
    driver.maximize_window()
    try:
        # driver.get("http://192.168.2.247:15100/")
        # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "UserName")),
        #                                 "No username").send_keys("jk_ceb9")
        # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "Password")), "No password").send_keys("asd123")
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form"]/div/div[3]/button')), "no login button.").click()
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menu"]/li/div[7]/span')),
        #                                 "no order manage.").click()
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="business"]/a')),
        #                                 "no order approve.").click()
        login = LoginPage(driver)
        login.get("http://192.168.2.247:15100/")
        login.username = "jk_ceb9"
        login.password = 'asd123'
        login.submit.click()
        menu = MainMenu(driver)
        menu.order_manage.click()
        menu.order_approve.click()
        sleep(1)
        driver.switch_to.frame("RIframe")
        order_manage = OrderManage(driver)
        orders = order_manage.order_list
        print(order_manage.get_order_list(orders))
        order_manage.select_all.click()
        order_manage.pass_order_all.click()
        driver.switch_to.default_content()
        print(order_manage.confirm_info.text)
        order_manage.pass_confirm.click()
        driver.switch_to.frame("RIframe")
        orders = order_manage.order_list
        print(order_manage.get_order_list(orders))
        # WebDriverWait(driver, 10, 0.5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#name')),
        #                                      "Cannot find search name.").send_keys("name")
        # WebDriverWait(driver, 10, 0.5).until(
        #     EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/table/thead/tr/th[1]/div/label')), "Cannot find selector.").click()
        driver.switch_to.default_content()
        sleep(1)
        menu.login_username.click()
        menu.logout.click()
        menu.logout_confirm.click()
        sleep(3)
    except Exception as e:
        print("Exception: " + str(e))
    finally:
        driver.quit()
        # driver.close()
