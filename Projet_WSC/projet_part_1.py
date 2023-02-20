from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from parsel import Selector
from selenium.webdriver.common.keys import Keys
from facebook_scraper import get_posts
from multiprocessing import Pool, cpu_count
import re
from requests import get
import pandas as pd
import numpy as np
import time
# from selenium_recaptcha import Recaptcha_Solver

def rechercheGoogle(localite,nombrePage):
    # chargement de webdriver et du navigateur
    
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # aller sur facebook
    driver.get('http://www.google.com')
    # recherche le champs de saisi
    search_query = driver.find_element_by_name('q')
    search_query.send_keys('site:facebook.com AND'+'"'+localite +'"AND "'+ "maison" +'"')
    search_query.send_keys(Keys.RETURN)
    time.sleep(30)
    # solver = Recaptcha_Solver(
    # driver=driver, # Your Web Driver
    # debug=False
    # )
    # solver.solve_recaptcha()




    time.sleep(30)
    test=True
    n=0
    lienGroup=[]
    while test:
        if n<nombrePage:
            try:
            ####### recuperer les liens des differents groupes
                facebook_urls = driver.find_elements_by_xpath("//*[@class='yuRUbf']/a")
                for url in facebook_urls:
                    if "facebook" in url.get_attribute("href"):
                        for id in range(len(url.get_attribute("href").split("/"))):
                            if url.get_attribute("href").split("/")[id]=="groups":
                                lienGroup.append(url.get_attribute("href").split("/")[id+1])
                                break    
                suivantpage = driver.find_element_by_id('pnnext')
                sleep(6)
                suivantpage.click()
                n=n+1
            except:
                    test=False
                    continue
        else:
                test=False

    return lienGroup

            
def postGroup(nbpage,idGroup):
    n=0
    ListPost=[]
    for post in get_posts(idGroup, cookies='cookies.txt', extra_info=True, pages=nbpage, options={"comments": False}):
        print(post)
        ListPost.append(post)
    return ListPost

ListIdGroup=rechercheGoogle("mbadon",1000)
nbpage=1
items=[(nbpage,x) for x in ListIdGroup]

def multiprocessing(postGroup , list):
    with Pool(cpu_count()) as p:
        print(cpu_count())
        rec=p.starmap( postGroup,list)    
        p.terminate()
        p.join()
        return rec
# Lanceur du script
if __name__ == '__main__':
        start_time = time.time()
        list = items
        ListeDictionnaire=multiprocessing(postGroup , list)
        # decomenter la ligne suivante pour afficher les valeurs
        #print(ListeDictionnaire)
        df = pd.concat([pd.DataFrame(lst) for lst in ListeDictionnaire])
        df.to_csv("output_mbon.csv", index= False)
        end_time = time.time() - start_time
        # Fin des traitement
        print("Temps total de compilation "+str(end_time))