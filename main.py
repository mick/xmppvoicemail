#!/usr/bin/env python
#
# Author: Mick Thompson (dthompson@gmail.com)
#
import os, urllib, logging, base64
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.api import xmpp
from google.appengine.api import urlfetch
import config


class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {}))


class CallHandler(webapp.RequestHandler):
    def post(self):
        From = self.request.get("From")
        CallStatus = self.request.get("CallStatus")

        xmpp.send_message(USERJID, "Call from: "+From+" status:"+CallStatus)
        path = os.path.join(os.path.dirname(__file__), 'receivecall.xml')
        template_vars = {"callbackurl": "/recording"}
        self.response.out.write(template.render(path, template_vars))



class PostRecording(webapp.RequestHandler):
    def post(self):
        RecordingUrl = self.request.get("RecordingUrl")
        TranscriptionStatus = self.request.get("TranscriptionStatus")
        Caller = self.request.get("Caller")
        TranscriptionText = self.request.get("TranscriptionText")

        ret = xmpp.send_message(config.USERJID, "New message: ("+Caller+")"+TranscriptionText+"Recording:"+RecordingUrl)
        if(ret == xmpp.NO_ERROR):
            self.response.out.write('')

class SMSHandler(webapp.RequestHandler):
    def post(self):
        From = self.request.get("From")
        To = self.request.get("To")
        Body = self.request.get("Body")

        FromJid = From + "@xmppvoicemail.appspotchat.com"

        xmpp.send_invite(config.USERJID, FromJid)
        xmpp.send_message(config.USERJID, Body, from_jid=FromJid)
        self.response.out.write("")


class XMPPHandler(webapp.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)

        form_fields = {
            "From": config.TWILIO_NUMBER,
            "To": message.to[0:12],
            "Body": message.body
            }
        form_data = urllib.urlencode(form_fields)

        twurl = "https://api.twilio.com/2010-04-01/Accounts/"+config.TWILIO_ACID+"/SMS/Messages"
        logging.debug('The twilio url: ' + twurl)

        result = urlfetch.fetch(url=twurl,
                                payload=form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded',
                                         "Authorization": "Basic %s" % (base64.encodestring(config.TWILIO_ACID + ":" + config.TWILIO_AUTH)[:-1]).replace('\n', '') })
        logging.debug('reply content: ' + result.content)


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/recording', PostRecording),
                                          ('/call', CallHandler),
                                          ('/sms', SMSHandler),
                                          ('/_ah/xmpp/message/chat/', XMPPHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
