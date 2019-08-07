import html2text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException
import os
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests import get
import datetime
import lxml.html
import re
from time import time
from time import sleep
from random import randint
from fake_useragent import UserAgent
from itertools import cycle
from urllib.request import Request, urlopen
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog

## A function to get a list of proxy ip
def getip():
    ua = UserAgent()  # From here we generate a random user agent
    proxies = []  # Will contain proxies [ip, port]
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')
    ipsoup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = ipsoup.find(id='proxylisttable')

    # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({
            'ip':
                row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string
        })
    global proxy_pool
    proxy_pool = cycle(proxies)
    scro_txt.insert(INSERT, 'New IP list added.\n')
    scro_txt.insert(INSERT, 'Current IP: ' + str(next(proxy_pool)) + '\n')
## The function the handle user inputs and store them.It will then also get all the url list from csv file
def submit():
    usr_name = var_usr_name.get()
    usr_pwd = var_usr_pwd.get()
    usr_path = var_usr_path.get()

    global usr_info
    usr_info = [usr_name, usr_pwd, usr_path]

    pd_url = pd.read_csv(usr_info[2])
    url_list = list(pd_url['Organization Name URL'])
    global url_info
    url_info = url_list

    scro_txt.insert(INSERT, 'Your information has been received.\n')
def to_csv():
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d-%H_%M")
    df["Organization Name"] = pd.Series(name)
    df["descrption"] = pd.Series(descrption)
    df["funding date"] = pd.Series(funding_date)
    df["funding type"] = pd.Series(funding_type)
    df["email"] = pd.Series(contact_email)
    df["phone number"] = pd.Series(contact_phone)
    df["CEO"] = pd.Series(ceo_name)
    df["CEO_contact"] = pd.Series(ceo_linkedin)
    df["CEO description"] = pd.Series(ceo_desc)
    df["CTO"] = pd.Series(cto_name)
    df["CTO_contact"] = pd.Series(cto_linkedin)
    df["CTO_description"] = pd.Series(cto_desc)
    # df.to_csv("7_16_GUI_Test.csv")
    df1 = pd.read_csv(usr_info[2])
    new_df = pd.merge(df1, df, on='Organization Name', how='left')
    new_df.to_csv(now_str + '.csv')
    messagebox.showinfo('Success', 'Conversion Complete!')

def scraper():
    cwd = os.getcwd()
    count = 0
    options = Options()
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(executable_path = cwd+'\\chromedriver')  # chrome_options=options, executable_path=r'C:/Users/Administrator/Desktop/WebScraping/chromedriver')
    driver.maximize_window()

    # driver.get('https://www.crunchbase.com/search/organization.companies/66e2f8bf5573fb73efb20c4ba2a512a0') #the url you want

    def check_exists_by_xpath(xpath):
        try:
            driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    ## Main function
    for url in url_info:

        scro_txt.see("end")
        window.update()
        count += 1
        print(url)
        scro_txt.insert(INSERT, url + '\n')

        # switch ips, one ip only runs 50 pages. This block of code will also close the old window and open a new window
        if count % 50 == 0:
            driver.quit()

            proxy = next(proxy_pool)
            # print(proxy)
            scro_txt.insert(INSERT, str(proxy) + '\n')
            # driver.close()
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--proxy-server = ' + str(proxy))
            driver = webdriver.Chrome(chrome_options=chrome_options,executable_path = cwd+'\\chromedriver')
            driver.maximize_window()

        driver.get(url)
        sleep(randint(2, 3))

        # This block of code detect if the block page come up. If so, it will click and hold the button and bypass the bot detector.
        if check_exists_by_xpath('//*[@id="px-captcha"]') is True:
            print("Block page appear")
            scro_txt.insert(INSERT, 'Block page appear\n')
            try:
                element2 = driver.find_element_by_xpath('//*[@id="px-captcha"]')
                ActionChains(driver).move_to_element(element2).perform()
                ActionChains(driver).move_by_offset(-500, 0).perform()
                ActionChains(driver).click_and_hold().perform()
                sleep(5)
                ActionChains(driver).release().perform()
            except:
                continue

        # This block detect if we got log off and will click on the close mark of the advertisment window
        if check_exists_by_xpath('//*[@id="cdk-overlay-0"]"]') is True:
            print('Got Logged Out ')
            scro_txt.insert(INSERT, 'Got Logged Out\n')
            button = driver.find_element_by_xpath("//*[@id='mat-dialog-0']/register-prompt/div/button")
            button.click()

        # This block will check if there is a log in button(only happen when we are not logged in) and log back in. It should be use
        # every time we switch ip(open new window) or when we got logged off by the website
        if check_exists_by_xpath(
                '/html/body/chrome/div/header/mat-toolbar[1]/span[3]/session-controls/div/a[1]/span') is True:

            try:
                myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'mat-input-0')))
                print("Page is ready!")
                scro_txt.insert(INSERT, 'Page is ready!\n')
                sleep(randint(2, 3))
            except TimeoutException:
                print('Loading took too much time!')
                scro_txt.insert(INSERT, 'Loading took too much time!\n')

            login = driver.find_element_by_xpath(
                "//html/body/chrome/div/header/mat-toolbar[1]/span[3]/session-controls/div/a[1]/span")

            '''
            ## this block of clock should also close the advertisment window
            if check_exists_by_xpath('//*[@id="mat-dialog-0"]/register-prompt/div"]') is True:
                print('Got Logged Out ')
                button = driver.find_element_by_xpath("//*[@id='mat-dialog-0']/register-prompt/div/button")
                button.click()
            '''
            try:
                login.click()
            except ElementClickInterceptedException:
                scro_txt.insert(INSERT, 'Advertisment Page appear\n')
                driver.get(url)

            ### Block page code

            if check_exists_by_xpath('//*[@id="px-captcha"]') is True:
                print("Block page appear")
                scro_txt.insert(INSERT, 'Block page appear\n')

                try:
                    element2 = driver.find_element_by_xpath('//*[@id="px-captcha"]')
                    ActionChains(driver).move_to_element(element2).perform()
                    ActionChains(driver).move_by_offset(-500, 0).perform()
                    ActionChains(driver).click_and_hold().perform()
                    sleep(5)
                    ActionChains(driver).release().perform()
                except:
                    continue

            try:
                elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'mat-input-2')))
                print("Page is ready!")
                scro_txt.insert(INSERT, 'Page is ready!\n')
            except TimeoutException:
                print('Loading took too much time!')
                scro_txt.insert(INSERT, 'Loading took too much time!\n')

            try:
                username = driver.find_element_by_id("mat-input-1")
            except:
                username = driver.find_element_by_id("mat-input-12")

            try:
                password = driver.find_element_by_id("mat-input-2")
            except:
                password = driver.find_element_by_id("mat-input-13")

            # username = driver.find_element_by_id("mat-input-1")
            # password = driver.find_element_by_id("mat-input-2")

            username.send_keys(usr_info[0])
            password.send_keys(usr_info[1])

            driver.find_element_by_css_selector("[type=submit]").click()
            sleep(randint(2, 3))

        # Another detection for the block page, if it appears, then click and bypass it.
        if check_exists_by_xpath('//*[@id="px-captcha"]') is True:
            print("Block page appear")
            scro_txt.insert(INSERT, 'Block page appear\n')
            try:
                element2 = driver.find_element_by_xpath('//*[@id="px-captcha"]')
                ActionChains(driver).move_to_element(element2).perform()
                ActionChains(driver).move_by_offset(-500, 0).perform()
                ActionChains(driver).click_and_hold().perform()
                sleep(5)
                ActionChains(driver).release().perform()
            except:
                continue

        # name
        try:
            titles_elements = driver.find_elements_by_xpath(
                """//*[@id="section-overview"]/mat-card/div[2]/image-with-fields-card/image-with-text-card/div/div/div[2]/div[1]""")[
                0]
            title = titles_elements.text
            name.append(title)
        except:
            continue

        # Description
        if check_exists_by_xpath("""//*[@id="section-overview"]/mat-card/div[2]/description-card/div""") is True:
            try:
                rm = driver.find_element_by_link_text("Read More")
                if rm.is_displayed():
                    rm.click()  # this will click the element if it is there
                    print("FOUND THE LINK CREATE ACTIVITY! and Clicked it!")
                    scro_txt.insert(INSERT, 'FOUND THE LINK CREATE ACTIVITY! and Clicked it!\n')
                    desp_elements = driver.find_elements_by_xpath(
                        """//*[@id="section-overview"]/mat-card/div[2]/description-card/div""")[0]
                    desp = desp_elements.text
                    descrption.append(desp)

            except NoSuchElementException:
                print("...")
                scro_txt.insert(INSERT, '...\n')
                desp_elements = \
                driver.find_elements_by_xpath("""//*[@id="section-overview"]/mat-card/div[2]/description-card/div""")[0]
                desp = desp_elements.text
                descrption.append(desp)
        else:
            desp = "None"
            descrption.append(desp)
            # sleep(randint(1,2))

        # funding date
        if check_exists_by_xpath(
                "//span[@class='component--field-formatter field-type-date_precision ng-star-inserted']") is True:
            funding_elements = driver.find_elements_by_xpath(
                "//span[@class='component--field-formatter field-type-date_precision ng-star-inserted']")[0]
            funding = funding_elements.text
            funding_date.append(funding)
        else:
            funding = "None"
            funding_date.append(funding)

        # funding type
        if check_exists_by_xpath("//a[contains(@href, 'last_funding_type')]") is True:
            funding_type_elements = driver.find_elements_by_xpath("//a[contains(@href, 'last_funding_type')]")[0]
            f_type = funding_type_elements.text
            funding_type.append(f_type)
        else:
            f_type = "None"
            funding_type.append(f_type)

        # contact_info_email & phone number  can be used

        if check_exists_by_xpath("//span[contains(text(),'@')]") is True:
            contact_elements = driver.find_elements_by_xpath("//span[contains(text(),'@')]")[0]
            contact_1 = contact_elements.text
            contact_email.append(contact_1)
        else:
            contact_1 = "None"
            contact_email.append(contact_1)

        # some problem to locate the phone number
        # str2 = "<>(111)111-1111</><>1(111)111-1111</><>+11111111111</><>111-111-1111</>"
        doc = driver.page_source
        phone_type1 = re.compile(r">([(][\d]{3}[)][\d]{3}-[\d]{4})<").findall(doc)
        phone_type2 = re.compile(r">([\d][(][\d]{3}[)][\d]{3}-[\d]{4})<").findall(doc)
        phone_type3 = re.compile(r">([\d]{10})<").findall(doc)
        phone_type4 = re.compile(r">(\+[\d]{11})<").findall(doc)
        phone_type5 = re.compile(r">([\d]{3}-[\d]{3}-[\d]{4})<").findall(doc)
        phone_type6 = re.compile(r">([(][\d]{3}[)]\s[\d]{3}-[\d]{4})<").findall(doc)
        phone = (phone_type1 + phone_type2 + phone_type3 + phone_type4 + phone_type5 + phone_type6)
        if len(phone) == 0:
            phone_1 = "None"
        else:
            phone_1 = phone[0]
        contact_phone.append(phone_1)

        # if WebDriverException:
        #    messagebox.showerror("Error","Web Brower is not reachable")

        # CTO name, contact info, and description
        if check_exists_by_xpath("//span[contains(text(), 'CTO')]/../../../a[1]") or check_exists_by_xpath(
                "//span[contains(text(), 'Chief Technology Officer')]/../../../a[1]") or check_exists_by_xpath(
                "//span[contains(text(), 'Chief Technical Officer')]/../../../a[1]") is True:
            print('CTO founded')
            scro_txt.insert(INSERT, 'CTO founded\n')
            if check_exists_by_xpath("//span[contains(text(), 'CTO')]/../../../a[1]") is True:
                cto_elements = driver.find_element_by_xpath("//span[contains(text(), 'CTO')]/../../../a[1]")
                try:
                    c_name = cto_elements.text
                    cto_name.append(c_name)
                    cto_elements.click()
                except StaleElementReferenceException:
                    print('StaleElementReferenceException appeared, trying to find element again')
                    cto_elements = driver.find_element_by_xpath("//span[contains(text(), 'CTO')]/../../../a")
                    c_name = cto_elements.text
                    cto_name.append(c_name)
                    cto_elements.click()

                sleep(0.5)

            elif check_exists_by_xpath("//span[contains(text(), 'Chief Technology Officer')]/../../../a[1]") is True:
                cto_elements = driver.find_element_by_xpath(
                    "//span[contains(text(), 'Chief Technology Officer')]/../../../a[1]")
                try:
                    c_name = cto_elements.text
                    cto_name.append(c_name)
                    cto_elements.click()
                except StaleElementReferenceException:
                    # print('StaleElementReferenceException appeared, trying to find element again')
                    scro_txt.insert(INSERT, 'StaleElementReferenceException appeared, trying to find element again\n')
                    cto_elements = driver.find_element_by_xpath("//span[contains(text(), 'CTO')]/../../../a")
                    c_name = cto_elements.text
                    cto_name.append(c_name)
                    cto_elements.click()

                sleep(0.5)

            elif check_exists_by_xpath("//span[contains(text(), 'Chief Technical Officer')]/../../../a[1]") is True:
                cto_elements = driver.find_element_by_xpath(
                    "//span[contains(text(), 'Chief Technical Officer')]/../../../a[1]")
                try:
                    c_name = cto_elements.text
                    cto_name.append(c_name)
                    cto_elements.click()
                except StaleElementReferenceException:
                    # print('StaleElementReferenceException appeared, trying to find element again')
                    scro_txt.insert(INSERT, 'StaleElementReferenceException appeared, trying to find element again\n')
                    cto_elements = driver.find_element_by_xpath("//span[contains(text(), 'CTO')]/../../../a")
                    c_name = cto_elements.text
                    cto_name.append(c_name)
                    cto_elements.click()

                sleep(0.5)

            # after the click action, block page might appear. So call the block page bypasser code.
            if check_exists_by_xpath('//*[@id="px-captcha"]') is True:
                print("Block page appear")
                scro_txt.insert(INSERT, 'Block page appear\n')
                try:
                    element2 = driver.find_element_by_xpath('//*[@id="px-captcha"]')
                    ActionChains(driver).move_to_element(element2).perform()
                    ActionChains(driver).move_by_offset(-500, 0).perform()
                    ActionChains(driver).click_and_hold().perform()
                    sleep(5)
                    ActionChains(driver).release().perform()
                except:
                    continue

            try:
                myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'mat-input-0')))
                print("Page is ready!")
                scro_txt.insert(INSERT, 'Page is ready!\n')
            except TimeoutException:
                print('Loading took too much time!')
                scro_txt.insert(INSERT, 'Loading took too much time!\n')

            '''link and description should be indepent'''
            # Getting the contact information and description of the cto here
            if check_exists_by_xpath(
                    "//*[@id='section-overview']/mat-card/div[2]/fields-card[2]/div/span[2]/field-formatter/link-formatter/a") is True:
                cto_contact = driver.find_element_by_xpath("//a[contains(@href, 'linkedin')]")
                cto_contact_info = cto_contact.get_attribute('href')
                cto_linkedin.append(cto_contact_info)

            elif check_exists_by_xpath(
                    "//*[@id='section-overview']/mat-card/div[2]/fields-card[3]/div/span[2]/field-formatter/link-formatter/a") is True:
                cto_contact = driver.find_element_by_xpath("//a[contains(@href, 'linkedin')]")
                cto_contact_info = cto_contact.get_attribute('href')
                cto_linkedin.append(cto_contact_info)

            else:
                cto_contact_info = 'none'
                cto_linkedin.append(cto_contact_info)

            if check_exists_by_xpath("//*[@id='section-overview']/mat-card/div[2]/description-card") is True:
                sleep(0.2)
                ct_desc = driver.find_element_by_xpath(
                    "//*[@id='section-overview']/mat-card/div[2]/description-card").text
                cto_desc.append(ct_desc)
            else:
                ct_desc = 'none'
                cto_desc.append(ct_desc)

            driver.get(url)

        else:
            print('No CTO')
            scro_txt.insert(INSERT, 'No CTO\n')
            c_name = 'none'
            contact_info = 'none'
            ct_desc = 'none'
            cto_name.append(c_name)
            cto_linkedin.append(contact_info)
            cto_desc.append(ct_desc)

        ### fixed by YY Get CEO name, description and contact information
        if check_exists_by_xpath("//span[contains(text(), 'CEO')]/../../../a") or check_exists_by_xpath(
                "//span[contains(text(), 'Chief Executive Officer')]/../../../a[1]") is True:
            print('CEO founded')
            scro_txt.insert(INSERT, 'CEO founded\n')

            if check_exists_by_xpath("//span[contains(text(), 'CEO')]/../../../a") is True:
                ceo_elements = driver.find_element_by_xpath("//span[contains(text(), 'CEO')]/../../../a")
                try:
                    ce_name = ceo_elements.text
                    ceo_name.append(ce_name)
                    ceo_elements.click()
                except StaleElementReferenceException:
                    # print('StaleElementReferenceException appeared, trying to find element again')
                    scro_txt.insert(INSERT, 'StaleElementReferenceException appeared, trying to find element again\n')
                    ceo_elements = driver.find_element_by_xpath("//span[contains(text(), 'CEO')]/../../../a")
                    ce_name = ceo_elements.text
                    ceo_name.append(ce_name)
                    ceo_elements.click()

                sleep(0.5)

            elif check_exists_by_xpath("//span[contains(text(), 'Chief Executive Officer')]/../../../a") is True:
                ceo_elements = driver.find_element_by_xpath(
                    "//span[contains(text(), 'Chief Executive Officer')]/../../../a")
                try:
                    ce_name = ceo_elements.text
                    ceo_name.append(ce_name)
                    ceo_elements.click()
                except StaleElementReferenceException:
                    # print('StaleElementReferenceException appeared, trying to find element again')
                    scro_txt.insert(INSERT, 'StaleElementReferenceException appeared, trying to find element again\n')
                    ceo_elements = driver.find_element_by_xpath("//span[contains(text(), 'CEO')]/../../../a")
                    ce_name = ceo_elements.text
                    ceo_name.append(ce_name)
                    ceo_elements.click()

                sleep(0.5)

            # deal with block page
            if check_exists_by_xpath('//*[@id="px-captcha"]') is True:
                print("Block page appear")
                scro_txt.insert(INSERT, 'Block page appear\n')
                try:
                    element2 = driver.find_element_by_xpath('//*[@id="px-captcha"]')
                    ActionChains(driver).move_to_element(element2).perform()
                    ActionChains(driver).move_by_offset(-500, 0).perform()
                    ActionChains(driver).click_and_hold().perform()
                    sleep(5)
                    ActionChains(driver).release().perform()
                except:
                    continue

            try:
                myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'mat-input-0')))
                print("Page is ready!")
                scro_txt.insert(INSERT, 'Page is ready!\n')
            except TimeoutException:
                print('Loading took too much time!')
                scro_txt.insert(INSERT, 'Loading took too much time!\n')

            # Find CEO's conatact information and description
            if check_exists_by_xpath(
                    "//*[@id='section-overview']/mat-card/div[2]/fields-card[2]/div/span[2]/field-formatter/link-formatter/a") is True:
                ceo_contact = driver.find_element_by_xpath("//a[contains(@href, 'linkedin')]")
                ceo_contact_info = ceo_contact.get_attribute('href')
                ceo_linkedin.append(ceo_contact_info)

            elif check_exists_by_xpath(
                    "//*[@id='section-overview']/mat-card/div[2]/fields-card[3]/div/span[2]/field-formatter/link-formatter/a") is True:
                ceo_contact = driver.find_element_by_xpath("//a[contains(@href, 'linkedin')]")
                ceo_contact_info = ceo_contact.get_attribute('href')
                ceo_linkedin.append(ceo_contact_info)

            else:
                ceo_contact_info = 'none'
                ceo_linkedin.append(ceo_contact_info)

            if check_exists_by_xpath("//*[@id='section-overview']/mat-card/div[2]/description-card") is True:
                c_desc = driver.find_element_by_xpath(
                    "//*[@id='section-overview']/mat-card/div[2]/description-card").text
                ceo_desc.append(c_desc)
            else:
                c_desc = 'none'
                ceo_desc.append(c_desc)

            #### another if for ceo descirption

        else:
            print('No CEO')
            scro_txt.insert(INSERT, 'No CEO\n')
            ce_name = 'none'
            ceo_contact_info = 'none'
            c_desc = 'none'
            ceo_name.append(ce_name)
            ceo_linkedin.append(ceo_contact_info)
            ceo_desc.append(c_desc)

        print(count)
        scro_txt.insert(INSERT, str(count) + '\n')
        # window.after(10000, update_display)
        scro_txt.insert(INSERT, '------------------------------\n')

    messagebox.showinfo('Complete', 'Mission Complete!')
def removed():
    scro_txt.delete(1.0, END)
def find_file():
    var_usr_path.set(filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("all files","*.*"),("jpeg files","*.jpg"))))

df = pd.DataFrame()
name = []
descrption = []
funding_date = []
funding_type = []
contact_email = []
contact_phone = []
ceo_name = []
ceo_linkedin = []
cto_name = []
cto_linkedin = []
ceo_desc = []
cto_desc = []

window = Tk()
window.title("Crunchbase Web Scraper")

lbl = Label(window, text="Welcome To The Crunchbase Scraper", font=('Arial', 15)).pack(pady=40)
lb2 = Label(window, text="Please Enter The Path of Your Crunchbase Output File:", fg='Blue', font=('Arial', 12)).pack()

var_usr_path = StringVar()
txt = Entry(window, textvariable=var_usr_path, width=80).pack(pady=5)
file_btn = ttk.Button(window, text="Find Your File",width=15,command = find_file).pack(pady = 5)

## Creating frame in the current windown
frame = Frame(window)
frame.pack()
frame_l = tk.Frame(frame)
frame_r = tk.Frame(frame)
frame_l.pack(side='left')
frame_r.pack(side='right')

name_lb = Label(frame_l, text="User Name:", fg='Blue').pack(pady=10)
pw_lb = Label(frame_l, text="Password:", fg='Blue').pack()

var_usr_name = StringVar()
user_txt = Entry(frame_r, textvariable=var_usr_name, width=30).pack(pady=10)

var_usr_pwd = StringVar()
pw_txt = Entry(frame_r, textvariable=var_usr_pwd, width=30, show='*').pack()

submit_btn = ttk.Button(window, text="Submit", command=submit).pack(pady=10)

lb4 = Label(window, text="Process Tracker:").pack()
scro_txt = scrolledtext.ScrolledText(window, width=75, height=20)
scro_txt.pack()

ip_btn = ttk.Button(window, text="Get IP", command=getip).pack(side='left', padx=20)
run_btn = ttk.Button(window, text="Run", width=10, command=scraper).pack(side='left', padx=180)
to_csv_btn = ttk.Button(window, text="Convert to CSV", width=25, command=to_csv).pack(side='right', padx=20)

# btn2 = Button(window, text="Remove",command = removed)
# btn2.grid(column=1, row=1)
window.bind('<Return>', lambda event: submit())
window.geometry('800x800+600+100')
# window.after(10000, update_display)
window.mainloop()