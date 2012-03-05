#!/usr/bin/python
# Licensed under the GNU General Public License v3
#Original feed_parser came from Akarsh Simhas script but I rewrote pretty much all of it
# since then
#2Mar2012 Added a scrollbar and fixed a few bugs
#4Mar2012 Added the ability to click links from rss feeds via Tkinter tags



from Tkinter import *
import webbrowser
import feedparser
import os
import threading
import time

class rssWindow(Frame):
    
    def __init__(self):
        Frame.__init__(self)
        self.master.title("Incoming RSS feeds")
        self._feed_list = ["http://rss.cnn.com/rss/cnn_world.rss", \
                           "http://feeds.bbci.co.uk/news/rss.xml?edition=int", \
                           "http://rss.cnn.com/rss/cnn_us.rss", \
                           "http://forum.codecall.net/external.php?type=rss2&lastpost=1", \
                           "http://www.dreamincode.net/rss/featured.php"]
        self._old_entries_file = os.environ.get("HOME") + "/.rss/old-feed-entries"
        self._links = []
        self._index = 0
        self._msgqueue = []
        self._t = None
        
        
        self._titleLabel = Label(self, text = "Die Enmand")
        self._titleLabel.grid()
        
        self._scrollbar = Scrollbar(self)
        self._scrollbar.grid(row = 1, column = 1, sticky=N+S)
        
        self._feedOutput = Text(self, state='disabled', wrap='word', width=80, height=24, yscrollcommand=self._scrollbar.set)
        self._feedOutput.grid(row=1, column=0)
        
        self._scrollbar.config(command=self._feedOutput.yview)
        
        self._button = Button(self, text = "Go", bg = "green", command = self._buttonPress)
        self._button.grid(row = 7, column = 0)
        
        #Added 04MAR12
        #Sets up the tag "a" for use with the links in our feeds
        self._feedOutput.tag_config("a", foreground="blue", underline=1)
        #Two lines below just make it so the hand cursor is displayed when you
        # hover over the tag
        self._feedOutput.tag_bind("a", "<Enter>", self._show_hand_cursor)
        self._feedOutput.tag_bind("a", "<Leave>", self._show_reg_cursor)
        #When the tag is clicked call the openurl method
        self._feedOutput.tag_bind("a", "<Button-1>", self._openurl)
        self._feedOutput.config(cursor="")
        
        self.grid()
    
    def _show_hand_cursor(self, event):
        self._feedOutput.config(cursor="hand2")
        
    def _show_reg_cursor(self, event):
        self._feedOutput.config(cursor="")
    
    def _buttonPress(self):
        if self._button["text"] == "Stop":
            self.stop_feed_refresh()
            self._button["bg"] = "green"
            self._button["text"] = "Go"
        else:
            self._feedServer()
            self._button["bg"] = "red"
            self._button["text"] = "Stop"
        
    def _feedServer(self):
        self.feed_refresh()   
        
    def stop_feed_refresh(self):
        self._t.cancel()
        
    def _openurl(self, event):
        idx = int(event.widget.tag_names(CURRENT)[1])
        webbrowser.open_new(self._links[idx])
        
    def _pull_link(self, msg):
        lst = msg.split(':', 1)
        addr = lst.pop().strip()
        info = lst.pop().strip()
        return (info, addr)
        
    def feed_refresh(self):
            
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
                    FILE.write( id + "\n" )
                    FILE.close()
                    self._msgqueue.append( entry.title.encode('utf-8') + " : " + entry.link.encode('utf-8') )
                if NextFeed:
                    break;
        self._feedOutput['state'] = 'normal'
        while len(self._msgqueue) > 0:
            msg = self._msgqueue.pop()
            
            #Added 04Mar12
            #This block of code sets up the links from the rss feeds to be clickable
            (info, addr) = self._pull_link(msg)
            self._feedOutput.insert('end', info)
            self._feedOutput.insert('end', " : ")
            #The "a" tag is defined in __init__
            self._feedOutput.insert('end', addr, ("a", str(self._index)))
            #Append each link in order
            self._links.append(addr)
            #Keep an index of how far we're in to our list of links
            self._index += 1
            
            self._feedOutput.insert('end', '\n')
            
        self._feedOutput['state'] = 'disabled'
        self._t = threading.Timer( 300.0, self.feed_refresh ) # TODO: make this static
        self._t.start()

def main():
    rssWindow().mainloop()

main()
