#!/usr/bin/python
# Licensed under the GNU General Public License v3
#Original feed_parser came from Akarsh Simhas script but I rewrote pretty much all of it
# since then
#2Mar2012 Added a scrollbar and fixed a few bugs
#4Mar2012 Added the ability to click links from rss feeds via Tkinter tags
#5Mar2012 Fixed a bug when the incoming feed had more than one : in the info
# used regex which should of been used to begin with
#30May2013 Added support for different OS paths

#Tested on: Python 3.3
#Requires feedparser package
#  feedparse requires setuptools package

from tkinter import *
import webbrowser
import re
import feedparser
import os
import threading
import time
import pickle as pickle


class rssWindow(Frame):
    
    def __init__(self):
        Frame.__init__(self)
        self.master.title("Incoming RSS feeds")
        self._feed_list = []
        self._old_entries_file = os.environ.get("HOME") + os.sep + ".rss" + os.sep + "old-feed-entries"
        self._settings_file = os.environ.get("HOME") + os.sep + ".rss" + os.sep + "settings.dat"
        self._links = []
        self._index = 0
        self._msgqueue = []
        self._t = None
        self._rssfeedvars = []

        #Check if our directory exists
        if not '.rss' in os.listdir(os.environ.get("HOME")):
            os.mkdir(os.environ.get("HOME") + os.sep + ".rss")
        
        #See if there's a entries file or not
        try:
            temp = open(self._old_entries_file, "r")
        except IOError:
            temp = open(self._old_entries_file, "w")
        temp.close()
        
        #See if there's a settings file or not
        try:
            self._fp = open(self._settings_file, "rb")
        except IOError:
            self._fp = open(self._settings_file, "wb")
        
        try:
            self._feed_list = pickle.load(self._fp)
        except IOError:
            print("Settings file not found")
            self._feed_list.append("http://rss.cnn.com/rss/cnn_world.rss")
        except EOFError:
            print("Generating default configuration")
            self._feed_list.append("http://rss.cnn.com/rss/cnn_world.rss")
        
        self._fp.close()
        
        #Menu
        #Added 22 MAR
        self.menubar = Menu(self)
        
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Settings", command=self.settings)
        self.menubar.add_cascade(label="File", menu=filemenu)
        
        self.menubar.add_command(label="Quit", command = quit)
        self.master.config(menu=self.menubar)
        
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
        
    #Added 22 Mar
    #settings window to put in rss feeds
    def settings(self):
        settwnd = Toplevel()
        settwnd.title("Settings")
        settwnd.grid()
        
        #Entry Vars
        self._rssfeedvars = []
        for i in range(8):
            self._rssfeedvars.append(StringVar())
        
        #Entry Fields
        entryfields = []
        for i in range(8):
            entryfields.append(Entry(settwnd, width=40 ,textvariable = self._rssfeedvars[i]))
            entryfields[i].grid()
            try:
                entryfields[i].insert(0, self._feed_list[i])
                self._rssfeedvars[i].set(self._feed_list[i])
            except IndexError:
                None
        
        savebutton = Button(settwnd, text = "Save", command = self._save)
        savebutton.grid()
        #Might add a quit button later but I'll need to setup a new pane for it
        #Button(settwnd, text = "Quit", command = settwnd.destroy).grid(column = 2)
        
    #Added 22 MAr
    #Save function for the settings menu item
    def _save(self):
        self._feed_list = []
        for i in range(8):
            if self._rssfeedvars[i].get() != '':
                self._feed_list.append(self._rssfeedvars[i].get())
        pickle.dump(self._feed_list, open(self._settings_file, "wb"))
    
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
        lst = re.split(r':[^//]', msg)
        addr = lst.pop().strip()
        info = " : ".join(lst)
        return (info, addr)
        
    def feed_refresh(self):
        FILE = open( self._old_entries_file, "r" )
        filetext = FILE.read()
        FILE.close()
        for feed in self._feed_list:
            NextFeed = False
            d = feedparser.parse( feed )
            for entry in d.entries:
                id = entry.link+entry.title
                if id in filetext:
                    NextFeed = True
                else:
                    FILE = open( self._old_entries_file, "a" )
                    FILE.write( id + "\n" )
                    FILE.close()
                    self._msgqueue.append( entry.title + " : " + entry.link)
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
