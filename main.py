from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import argparse
import time
import os
from webdriver_manager.chrome import ChromeDriverManager as CM
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
from math import *
import shutil

#----------------------------------------------------------------------------------------

#  ___    ___    _  _   ___   ___    ___ 
# / __|  / _ \  | \| | | __| |_ _|  / __|
#| (__  | (_) | | .` | | _|   | |  | (_ |
# \___|  \___/  |_|\_| |_|   |___|  \___|

tiktok_sessionID = "your_tiktok_sessionid" #tiktok sessionid (Se rendre sur https://www.tiktok.com/ - Se connecter - Recuperer la valeur du cookie "sessionid")
uploadInterval = 60 #Interval entre la publication de deux videos en secondes
toDownload = ["https://www.youtube.com/watch?v=2lAe1cqCOXo",
 "https://www.youtube.com/watch?v=8qTQbk2A02M",
 "https://www.youtube.com/watch?v=FzytYMcq-Qg"] #Liens des vidéos a publier sous forme d'un tableau ex : ["https://...", "https://...","https://..."]
hashtags = "#tiktok #fyp" #hashtags sous la video
#----------------------------------------------------------------------------------------

class TikTokBot:
    def __init__(self, who_can_view, video_path, caption):
        path = os.path.dirname(os.path.abspath(__file__))
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(options=options,  executable_path=CM().install())
        self.driver.set_window_size(1440, 900)
        self.executor_url = self.driver.command_executor._url
        self.session_id = self.driver.session_id
        print(self.executor_url, self.session_id)
        self.driver.get('https://tiktok.com')
        self.driver.add_cookie({'name' : 'sessionid', 'value' : tiktok_sessionID, 'domain' : '.tiktok.com'})
        time.sleep(1)
        self.driver.get('https://www.tiktok.com/upload/?lang=en')
        self.url = self.driver.current_url
        print(self.url)

        # takes you to the upload page
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0,500);")

        # upload video from files
        while True:
            try:
                self.driver.find_element_by_xpath('//input[contains(@name, "upload-btn")]').send_keys(video_path)
                break
            except NoSuchElementException:
                time.sleep(2)

        # set caption
        self.driver.find_element_by_xpath('//div[contains(@class, "notranslate public-DraftEditor-content")]').send_keys(caption)

        # make sure video is uploaded
        while True:
            try:
                video = self.driver.find_element_by_css_selector('video[src^="blob"]')
                source = video.get_attribute('src')
                print('video uploaded, wait for submitting')
                break
            except NoSuchElementException:
                print('video uploading...')
                time.sleep(10)

        # click submit
        print('submitting...')
        self.driver.find_element_by_xpath('//button[contains(text(), "Post")]').click()
        print('DONE! ' + caption + " is published")
        print("Wait " + str(uploadInterval) + " seconds before uploading next video...")
        time.sleep(uploadInterval)
        self.driver.close()
        

for i in toDownload:
    yt = YouTube(i)
    yt.streams.first().download('./videos/brut/uncuted')

    title = yt.title.replace("'", "")
    title = title.replace("'", "")
    title = title.replace(":", "")
    title = title.replace("#", "")
    title = title.replace("|", "")

    clip = VideoFileClip("./videos/brut/uncuted/" + title +".mp4")
    parts = ceil(clip.duration/50)
    for x in range(parts):
        part = x + 1
        if(x == parts-1):
            end = clip.duration
        else:
            end = part*50

        start = x*50
        ffmpeg_extract_subclip("./videos/brut/uncuted/" + title + ".mp4", start, end, targetname="./videos/cut/unposted/" + title +"$$part" + str(part).zfill(2) + ".mp4") 
        time.sleep(5)
        titleComplete = title + " - part " + str(part)
        TikTokBot(who_can_view="Public", video_path="./videos/cut/unposted/" + title + "$$part" + str(part).zfill(2) + ".mp4", caption=titleComplete + " " + hashtags)
        time.sleep(1)
        os.remove("./videos/cut/unposted/" + title + "$$part" + str(part).zfill(2) + ".mp4")
    os.remove("./videos/brut/uncuted/" + title +".mp4")

