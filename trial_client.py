#!/usr/bin/env python
# Usage:
#
# Goto System Preferences > Security & Privacy > Accessibility and add
# Python to apps allowed to control your computer. If it is not in the
# list, the easiest is to run this file first and it should appear.

# from pprint import pprint
from AppKit import NSApplication, NSApp
from Foundation import NSObject, NSLog
from Cocoa import NSEvent, NSKeyDownMask
from PyObjCTools import AppHelper

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        mask = NSKeyDownMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, handler)

def handler(event):
    try:
        # NSLog(u"%@", event)
        # pprint(vars(event))
        # print(event)
        pass
    except KeyboardInterrupt:
        AppHelper.stopEventLoop()

def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    AppHelper.runEventLoop()

if __name__ == '__main__':
    main()
