#!/usr/bin/python
# Licensed under the GNU General Public License v3
#Some of the feed parser came from Akarsh Simhas script but I rewrote most of it


from Tkinter import *
import feedparser
import os
import threading
import time

class rssWindow(Frame):
    
    def __init__(self):
        Frame.__init__(self)
        self.master.title("Incoming RSS feeds")
        self.grid()
        #self._labels = []
        self._feed_list = ["http://rss.cnn.com/rss/cnn_world.rss", \
                           "http://feeds.bbci.co.uk/news/rss.xml?edition=int", \
                           "http://rss.cnn.com/rss/cnn_us.rss", \
                           "http://forum.codecall.net/external.php?type=rss2&lastpost=1", \
                           "http://www.dreamincode.net/rss/featured.php"]
        self._old_entries_file = os.environ.get("HOME") + "/.b0t/old-feed-entries"
        self._msgqueue = []
        self._t = None
        
        self._titleLabel = Label(self, text = "Die Enmand")
        self._titleLabel.grid()
        
        self._feedOutput = Label(self, text = "")
        self._feedOutput.grid(row = 1, column = 0, rowspan = 6, columnspan = 6)
        
        self._button = Button(self, text = "Get", bg = "green", command = self._feedServer)
        self._button.grid(row = 7, column = 1)
        
    def _feedServer(self):
        #self._button["bg"] = "green"
        #self._button["text"] = "On"
        
        self.feed_refresh()   
        
        while len(self._msgqueue) > 0:
            msg = self._msgqueue.pop()
            self._feedOutput["text"] += msg
        #self._feedOutput["text"] += "Done\n"
        self.stop_feed_refresh()
        
    def stop_feed_refresh(self):
        self._t.cancel()
        
    def feed_refresh(self):
        #print "Test"
            
        FILE = open( self._old_entries_file, "r" )
        filetext = FILE.read()
        FILE.close()
        for feed in self._feed_list:
            NextFeed = False
            d = feedparser.parse( feed )
            for entry in d.entries:
                id = entry.link.encode('utf-8')+entry.title.encode('utf-8')
                if id in filetext:
                    NextFeed = True
                else:
                    FILE = open( self._old_entries_file, "a" )
                    #print entry.title + "\n"
                    FILE.write( id + "\n" )
                    FILE.close()
                    self._msgqueue.append( entry.title.encode('utf-8') + " : " + entry.link.encode('utf-8') )
                if NextFeed:
                    break;
        self._t = threading.Timer( 900.0, self.feed_refresh ) # TODO: make this static
        self._t.start()
    
    def output_feeds(self):
        while len(msgqueue) > 0:
            msg = msgqueue.pop()
            
def main():
    rssWindow().mainloop()

main()
