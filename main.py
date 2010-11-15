#!/usr/bin/env python
#
# Author: Mick Thompson (dthompson@gmail.com)
#
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.api import xmpp


# change this to the JID of your Xmpp account (example: dthompson@gmail.com)
USERJID = "you@domain.com"

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

        ret = xmpp.send_message(USERJID, "New message: ("+Caller+")"+TranscriptionText+"Recording:"+RecordingUrl)
        if(ret == xmpp.NO_ERROR):
            self.response.out.write('')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/recording', PostRecording),
                                          ('/call', CallHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
