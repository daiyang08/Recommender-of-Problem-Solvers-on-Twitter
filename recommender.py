import wx
import os
import sys

import nltk
import twitter
from nltk.corpus import webtext
from nltk.corpus import gutenberg
from nltk.corpus import stopwords

import main_process


# parse_qsl moved to urlparse module in v2.6
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl

import oauth2 as oauth

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'

consumer_key    = 'TuLPEoqwSkiVreWEODQ6tA'
consumer_secret = 'LnPHHrMOiPVX5PlObJKryROYtdC3475Xq0WJ2tHlJHM'

if consumer_key is None or consumer_secret is None:
  print 'You need to edit this script and provide values for the'
  print 'consumer_key and also consumer_secret.'
  print ''
  print 'The values you need come from Twitter - you need to register'
  print 'as a developer your "application".  This is needed only until'
  print 'Twitter finishes the idea they have of a way to allow open-source'
  print 'based libraries to have a token that can be used to generate a'
  print 'one-time use key that will allow the library to make the request'
  print 'on your behalf.'
  print ''
  sys.exit(1)

class Application(wx.Frame): 
    def __init__(self, parent): 
        wx.Frame.__init__(self, parent, -1, 'Recommender of problem solvers__Twitter - beta 0.5', size=(470, 500)) 
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL) 
        panel.SetSizer(sizer) 
        txt = wx.StaticText(panel, -1, 'Please make sure you have log in your Twitter account!', pos=(20,10))
        txt2 = wx.StaticText(panel, -1, 'Please click the hyperlink below to authorize our App!', pos=(20,30)) 
        self.Centre() 
        self.Show(True)
        #Pinremindlbl = wx.StaticText(panel, -1, "Please input the generized Pin Code below, thanks! ", pos=(20,100))
        #PINlbl = wx.StaticText(panel, -1, "Pin Code: ", pos=(92,135))
        #self.PIN = wx.TextCtrl(panel, -1, " ",size=(250,25), pos=(160, 130))
        Pinremindlbl = wx.StaticText(panel, -1, "Please input the generized Pin Code below, clear the default space! ", pos=(20,100))
        PINlbl = wx.StaticText(panel, -1, "Pin Code: ", pos=(20,135))
        self.PIN = wx.TextCtrl(panel, -1, " ",size=(80,25), pos=(88, 130))
        dscrptremindlbl = wx.StaticText(panel, -1, "Please input your problem description below! ", pos=(20,170))
        dscrptlbl = wx.StaticText(panel, -1, "Problem Description: ", pos=(20,200))
        self.dscrpt = wx.TextCtrl(panel, -1, " ",size=(250,36), pos=(160, 200), style=wx.TE_MULTILINE)
        
        

        divlbl = wx.StaticText(panel, -1, "===============================================", pos=(0,290))
        namelbl = wx.StaticText(panel, -1, "Choose a name to send a direct message: \nPlease clear the default space!", pos=(20,310))
        self.sendname = wx.TextCtrl(panel, -1, " ",size=(120,25), pos=(20, 345))
        messagelbl = wx.StaticText(panel, -1, "sending message: ", pos=(20,380))
        self.sendmessage = wx.TextCtrl(panel, -1, " ",size=(250,36), pos=(140, 380), style=wx.TE_MULTILINE)
        
        self.text = 'No description input??'

        okbutton = wx.Button(panel, -1, "Ok", pos=(100,260))
        cancelbutton = wx.Button(panel, -1, "Cancel", pos=(280,260))
        sendbutton = wx.Button(panel, -1, "Send", pos=(100,440))
        cancelbutton2 = wx.Button(panel, -1, "Cancel", pos=(280,440))
        #self.Bind(wx.EVT_BUTTON, self.OnLogin, loginbutton)
        self.Bind(wx.EVT_BUTTON, self.OnOk, okbutton)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, cancelbutton)
        self.Bind(wx.EVT_BUTTON, self.OnSend, sendbutton)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, cancelbutton2)

        self.signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
        #print self.signature_method_hmac_sha1
        self.oauth_consumer = oauth.Consumer(key='TuLPEoqwSkiVreWEODQ6tA', secret='LnPHHrMOiPVX5PlObJKryROYtdC3475Xq0WJ2tHlJHM')
        self.oauth_client = oauth.Client(self.oauth_consumer)

        resp, content = self.oauth_client.request(REQUEST_TOKEN_URL, 'GET')
        self.resp = resp
        self.content = content
        if self.resp['status'] != '200':
        	print 'Invalid respond from Twitter requesting temp token: %s' % self.resp['status']
        else:
        	self.request_token = dict(parse_qsl(self.content))

        self.Oauth_url = AUTHORIZATION_URL + '?oauth_token=' + self.request_token['oauth_token']
        link = wx.HyperlinkCtrl(parent=panel,id = -1, url=self.Oauth_url, label='Autherization', pos=(150, 60))
        self.api = {}

    def OnOk(self, event):
        #print 'main_process';
        self.text = self.dscrpt.GetValue()
        pincode = self.PIN.GetValue()

        self.token = oauth.Token(self.request_token['oauth_token'], self.request_token['oauth_token_secret'])
        self.token.set_verifier(pincode)
        #pincode = pincode[0:(len(pincode)-1)]
        self.oauth_client  = oauth.Client(self.oauth_consumer, self.token)
        #resp2, content2 = self.oauth_client.request(ACCESS_TOKEN_URL, method='POST', body='oauth_callback=oob&oauth_verifier=%s' % str(pincode))
        resp2, content2 = self.oauth_client.request(ACCESS_TOKEN_URL, method='POST', body='oauth_callback=oob&oauth_verifier=%s' % str(pincode))
        #print content2;

        self.resp = resp2
        self.content = content2

        self.access_token  = dict(parse_qsl(self.content))
        #print self.oauth_consumer
        if self.resp['status'] != '200':
            print 'The request for a Token did not succeed: %s' % self.resp['status']
            print self.access_token
        else:
            self.oauth_token = self.access_token['oauth_token']
            self.oauth_token_secret = self.access_token['oauth_token_secret']
            #loginlbl = wx.StaticText(self.panel, -1, "Log in success!", pos=(320,135))
            self.api = twitter.Api(consumer_key='TuLPEoqwSkiVreWEODQ6tA',consumer_secret='LnPHHrMOiPVX5PlObJKryROYtdC3475Xq0WJ2tHlJHM',access_token_key=self.oauth_token,access_token_secret=self.oauth_token_secret)

            #print self.oauth_token
            #print self.oauth_token_secret

    	main_process.main_process(self.api,self.text, self.oauth_token, self.oauth_token_secret)

    def OnCancel(self, event):
        self.Destroy()

    def OnSend(self,event):
        name_to_send = self.sendname.GetValue()
        message_to_send = self.sendmessage.GetValue()
        
        followers = self.api.GetFollowers()
        for person in followers:
            if person.name == name_to_send:
                self.api.PostDirectMessage(message_to_send, user_id = person.id)
                break
        print 'message sent';
        #print api.

if __name__=='__main__':
    app = wx.App(redirect=False)
    Application(None)
    app.MainLoop()
    #app = wx.PySimpleApp()
    
    #print 'sbl'
    #print myapp.text
    
    #print myapp.text
    #myapp.ShowModal()
    #text = myapp.text
    

#app = wx.App(0) 

#app.MainLoop()
