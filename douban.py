#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-10-09 17:11:42
# @Author  : Linsir (vi5i0n@hotmail.com)
# @Link    : http://Linsir.sinaapp.com

import urllib
import urllib2
import cookielib
import re
import random
import time
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

#ACCOUNT
EMAIL = ''
PASSWORD = ''

#SOFA
CONTENT = [
            '天苍苍野茫茫，风吹草低见牛羊。',
            '说的有道理。',
          ]

class NoExceptionCookieProcesser(urllib2.HTTPCookieProcessor):
  def http_error_403(self, req, fp, code, msg, hdrs):
    return fp
  def http_error_400(self, req, fp, code, msg, hdrs):
    return fp
  def http_error_500(self, req, fp, code, msg, hdrs):
    return fp

class douban_robot:

    def __init__(self):
            self.ck = None
            self.data = {
                    "form_email": EMAIL,
                    "form_password": PASSWORD,
                    "source": "index_nav",
                    "remember": "on"
            }
            self.cookieFile = "cookies_saved.txt";
            self.cookie = cookielib.LWPCookieJar(self.cookieFile);
            #will create (and save to) new cookie file
            self.login_url = 'http://www.douban.com/accounts/login'
            self.opener = urllib2.build_opener(NoExceptionCookieProcesser(self.cookie))
            self.opener.addheaders = [("User-agent","Mozilla/5.0 (Windows NT 6.1) \
                AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11)")]
            # self.opener.addheaders = [("Origin", "http://www.douban.com")]
            self.load_cookies()
            self.get_ck()
            self.get_uid()
    def load_cookies(self):
        try:
            self.cookie.load(self.cookieFile)
            print "loading cookies.."
        except:
            print "The cookies file is not exist."
            self.login_douban()
            self.load_cookies()

    def get_uid(self):
        #open a url to get the value of ck.
        response = self.opener.open('http://www.douban.com')
        for c in list(self.cookie):
            if c.name == 'dbcl2':
                self.uid = c.value.strip('"').split(':')[0]
                print "uid:%s" %self.uid
                break
        if self.uid:
            print 'The uid is %s.' % self.uid
        else:
            print 'uid is out of date.'

    def get_ck(self):
        #open a url to get the value of ck.
        response = self.opener.open('http://www.douban.com')
        for c in list(self.cookie):
            if c.name == 'ck':
                self.ck = c.value.strip('"')
                print "ck:%s" %self.ck
                break

        if self.ck:
            print 'The ck is update.'

        else:
            print 'ck is out of date.'
            self.login_douban()
            self.load_cookies()
            self.get_ck()

    #utils
    def get_captcha(self):
        im =  Image.open('captcha.jpg')
        frame = im.load()
        width, height = im.size
        #threshold = 21
        threshold = 27
        for i in range(0, width):
            for j in range(0, height):
                p = frame[i, j]
                r, g, b = p
                if r > threshold or g > threshold or b > threshold:
                    frame[i, j] = (255, 255, 255)
                else:
                    frame[i, j ] = (0, 0, 0)
        window = 1
        """ 中值滤波移除噪点
            """
        if window == 1:
            # 十字窗口
            window_x = [1, 0, 0, -1, 0]
            window_y = [0, 1, 0, 0, -1]
        elif window == 2:
            # 3*3矩形窗口
            window_x = [-1,  0,  1, -1, 0, 1, 1, -1, 0]
            window_y = [-1, -1, -1,  1, 1, 1, 0,  0, 0]

        width, height = im.size
        frame = im.load()
        for i in xrange(width):
            for j in xrange(height):
                box = []
                black_count, white_count =  0, 0
                for k in xrange(len(window_x)):
                    d_x = i + window_x[k]
                    d_y = j + window_y[k]
                    try:
                        d_point = frame[d_x, d_y]
                        if d_point == (0, 0, 0):
                            box.append(1)
                        else:
                            box.append(0)
                    except IndexError:
                        frame[i, j] = (255, 255, 255)
                        continue

                box.sort()
                if len(box) == len(window_x):
                    mid = box[len(box)/2]
                    if mid == 1:
                        frame[i, j ] = (0, 0, 0)
                    else:
                        frame[i, j] = (255, 255, 255)
        im.save('captcha.jpg')
        reccode_captcha =  pytesseract.image_to_string(im, lang='eng', config='-psm 6')
        reccode_captcha_search =  ''.join(re.findall(r'([a-z])', reccode_captcha.lower()))
        print 'Google程序破解的验证码[%s],优化后的验证码[%s],骚年只要是正确的英文单词就破解成功了Ooo' % (reccode_captcha, reccode_captcha_search)
        return reccode_captcha_search

    def login_douban(self):
        '''
        login douban and save the cookies into file.

        '''
        response = self.opener.open(self.login_url, urllib.urlencode(self.data))
        if 403 == response.code :
            raise Exception("意外中断了.Ooo")
        html = response.read()

        # fp = open("1.html","wb")
        # fp.write(html)
        # fp.close

        imgurl = re.compile(r'<img id="captcha_image" src="(.+?)" alt="captcha"').findall(html)
        if imgurl:
            #download the captcha_image file.
            print "The captcha_image link is %s" %imgurl[0]
            data = self.opener.open(imgurl[0]).read()
            # f = file("captcha.jpg","wb")
            # f.write(data)
            # f.close()

            captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
            if captcha:
                vcode=raw_input('打开上面链接的图片的验证码是：')
                self.data["captcha-solution"] = vcode
                self.data["captcha-id"] = captcha.group(1)
                self.data["user_login"] = "登录"
                #验证码验证
                response = self.opener.open(self.login_url, urllib.urlencode(self.data))

        #登录成功
        if response.geturl() == "http://www.douban.com/":
            print 'login success !'
            self.cookie.save();
        else:
            return False
        return True
    #utils

    def new_topic(self, group_id, title, content):

        group_url = "http://www.douban.com/group/" + group_id
        post_url = group_url + "/new_topic"
        post_data = urllib.urlencode({
            'ck':self.ck,
            'rev_title': title ,
            'rev_text': content,
            'rev_submit':'好了，发言',
            })
        request = urllib2.Request(post_url)

        # request.add_header("Origin", "http://www.douban.com")
        request.add_header("Referer", post_url)
        response = self.opener.open(request, post_data)
        if response.geturl() == group_url:
            print 'Okay, Success !'
            return True
        return False


    def talk_statuses(self, content = '(⊙o⊙)…'):

        post_data = urllib.urlencode({
            'ck' : self.ck,
            'comment' : content,
            })

        request = urllib2.Request("http://www.douban.com/")
        # request.add_header("Origin", "http://www.douban.com")
        request.add_header("Referer", "http://www.douban.com/")
        self.opener.open(request, post_data)


    def send_mail(self, id ,content = 'Hey,girl !'):

        post_data = urllib.urlencode({
           "ck" : self.ck,
           "m_submit" : "好了，寄出去",
           "m_text" : content,
           "to" : id,
           })
        request = urllib2.Request("http://www.douban.com/doumail/write")
        # request.add_header("Origin", "http://www.douban.com")
        request.add_header("Referer", "http://www.douban.com/doumail/write")
        self.opener.open(request, post_data)

    def no_robot(self):
        print '进入防机器人破解阶段......'
        html = self.opener.open("http://www.douban.com/misc/sorry").read()
        imgurl = re.compile(r'<img src="(.+?)" alt="captcha"').findall(html)
        post_data = {
            "ck" : self.ck,
            "submit_btn" : "我真的不是程序"
        }
        if imgurl:
            data = self.opener.open(imgurl[0]).read()
            f = file("captcha.jpg","wb")
            f.write(data)
            f.close()
            captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
            captcha_code = self.get_captcha()
            post_data["captcha-solution"] = captcha_code
            post_data["captcha-id"] = captcha.group(1)
        post_data = urllib.urlencode(post_data)
        self.opener.open("http://www.douban.com/misc/sorry", post_data)

    def get_join_groups(self):
        group_join_url = "http://www.douban.com/group/people/" + self.uid +"/joins"
        response = self.opener.open(group_join_url)
        html = response.read()
        if 403 == response.code :
            raise Exception("403意外中断了.Ooo")
        else:
            join_groups = re.findall(r'<a href="http://www.douban.com/group/(\w+?)/".*?<img',
                        html, re.DOTALL)
            return join_groups

    def sofa(self,
        group_id,
        content=CONTENT
        ):

        group_url = "http://www.douban.com/group/" + group_id +"/#topics"
        response = self.opener.open(group_url)
        if 403 == response.code :
            raise Exception("403意外中断了.Ooo")
        html = response.read()
        topics = re.findall(r'topic/(\d+?)/.*?class="">.*?<td nowrap="nowrap" class="">(.*?)</td>',
                    html, re.DOTALL)
        for item in topics:
            if item[1] == '':
                print '日你嘴，在小组[%s]发现新帖[%s]...Ooo' % (group_id, item[0])
                response = self.opener.open("http://www.douban.com/group/topic/" + item[0])
                if 403 == response.code :
                    raise Exception("403意外中断了.Ooo")
                html = response.read()
                imgurl = re.compile(r'<img id="captcha_image" src="(.+?)" alt="captcha"').findall(html)
                post_data = {
                    "ck" : self.ck,
                    "rv_comment" : random.choice(content),
                    "start" : "0",
                    "submit_btn" : "加上去"
                }
                if imgurl:
                    data = self.opener.open(imgurl[0]).read()
                    f = file("captcha.jpg","wb")
                    f.write(data)
                    f.close()
                    captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
                    captcha_code = self.get_captcha()
                    post_data["captcha-solution"] = captcha_code
                    post_data["captcha-id"] = captcha.group(1)
                post_data = urllib.urlencode(post_data)
                self.opener.open("http://www.douban.com/group/topic/" + item[0] + "/add_comment#last?", post_data)



    def get_joke(self):
        html = urllib2.urlopen('http://www.xiaohuayoumo.com/').read()
        result = re.compile(r']<a href="(.+?)">(.+?)</a></div>.+?', re.DOTALL).findall(html)
        for x in result[:1]:
            title = x[1]
            # print title
            joke_url = 'http://www.xiaohuayoumo.com' + x[0]
            page = self.opener.open(joke_url).read()
            result = re.compile(r'content:encoded">(.+?)<a href.+?</a>(.+?)</div></div></div></div>',
                        re.DOTALL).findall(page)
            for x in result[:1]:
                content = x[0] + x[1]
                content = re.sub(r'</?\w+[^>]*>',' ',content)
                # print content
        return title, content



if __name__ == '__main__':
    # titile, content = app.get_joke()
    # content = '又到了笑话时间了~\(≧▽≦)/~\n' + content
    # if titile and content:
    #     print app.new_topic("cd", titile, content)

    #app.talk_statuses('Hello.it\'s a test message using python.')
    # app.send_mail(66902522)
    #shenzhen
    while 1:
        app = None
        try:
            app = douban_robot()
            join_groups = app.get_join_groups()
            while 1:
                try:
                    for join_group in join_groups:
                        print '进入[%s]小组Ooo' % join_group
                        app.sofa(join_group)
                    time.sleep(1)
                except Exception,e:
                    raise Exception("403意外中断了.Ooo")
        except Exception,e:
            print '你被发现是机器人了，正在识别防机器人验证码......'
            app.no_robot()
