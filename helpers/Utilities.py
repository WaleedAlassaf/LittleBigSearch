import os, math
import sys
import subprocess
from    tkmacosx import Button


class GlobalVars:
    BGColorDark   = "#1e1e1e"
    BGColorLight  = "#2f2f2f"
    logoBlue      = "#2cb4e8"
    heartRed      = "#ff194a"

    currentPath = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])


class Utilities:
    
    @staticmethod
    def openFile(path):
        try:
            subprocess.call(["open", "-R", path])
        except:
            print("Failed to open folder")
    
    
    @staticmethod
    def splitLevelsToLists(levels, splitSize = 50):
        #Splits the large levels list into smaller lists of 50 element each
        levels = list(levels)
        x = int(math.ceil(len(levels) / splitSize))
        k, m = divmod(len(levels), x)
        return list( (levels[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(x)) )
    
    @staticmethod
    def makeLabel(textVar, master = None, activeColor = None, backgroundColor = GlobalVars.BGColorDark):
        label = Button()
        if master != None: label = Button(master= master)
        if activeColor != None: label.config(activebackground= activeColor)

        label.config(textvariable      = textVar,
                    bd                 = 0,
                    borderless         = 1,
                    highlightthickness = 0,
                    highlightcolor = GlobalVars.BGColorDark,
                    focuscolor         = '',
                    fg                 = "White",
                    bg            = backgroundColor,
                    font          = ('Helvatical bold',15))
        return label
    
    @staticmethod
    def makeButton(master     = None, 
                  text        = None,
                  command     = None,
                  buttonColor = GlobalVars.BGColorLight,
                  activeColor = GlobalVars.logoBlue):

        btn = Button()
        if master  != None: btn = Button(master= master)
        if command != None: btn.config(command= lambda: command())
        if text    != None: btn.config(text = text)
        
        btn.config( bd                  = 0,
                    borderless          = 1,
                    focuscolor          = '',
                    fg                  = "white",
                    cursor              = "hand2",
                    highlightbackground = GlobalVars.BGColorDark,
                    bg                  = buttonColor,
                    activebackground    = activeColor)
        
        return btn        