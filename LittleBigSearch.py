import tkinter           as tk
import os, shutil,threading, ttkthemes, random
from   genericpath       import exists
from   tkinter           import Canvas, Frame, ttk
from   tkinter.constants import VERTICAL
from   functools         import partial
from   PIL               import Image, ImageTk
from   SFOParser         import LevelParser, ParserReturns
from idlelib.tooltip     import Hovertip

from helpers.Utilities import GlobalVars as GB
from helpers.Utilities import Utilities as util
from SavedLevels       import SavedLevels
from Settings.OptionsManager import OptionsManager

class LittleBigSearchGUI():
    def __init__(self, master: tk.Tk, matchedLevels = [], settings = 0, savedLevels = 0) -> None:
        
        self.options = OptionsManager(self.errorCallback, self.clearRandomLevelsPool)
        
        self.scrollerCanvas  = tk.Canvas()
        self.scrollerBase   = Frame()
        
        self.levelParser        = LevelParser()
        self.matchedLevels      = matchedLevels
        
        self.hasMoreThanOnePage = False
        self.isSearching        = False 
        self.isFirstRun         = True
        
        self.currentPageLevels  = []
        self.currentPage        = 0
        
        self.generateRandomPool = False
        self.randomLevelsPool   = []

        self.globeFrameIndex = 0 
        self.globeFrames   = util.loadGif(framesCount=GB.GLOBE_GIF_FRAME_COUNT,
                                               gifDir= "images/animation/", gifName= "earth")     
        
        
        self.master = master
        self.master.title("By @SackBiscuit v1.1.4.1")
        self.master.iconbitmap(default=util.resourcePath("images\\icon.ico"))
        self.master.configure(bg= GB.BGColorDark)

        ttkthemes.themed_style.ThemedStyle(theme="adapta")

        self.levelHeart = util.resize(image = util.resourcePath("images\\UI\\lbpLevelHeart.png"), height=30, width=30)
        
        # _ UI _______________________

        self.mainCanvas = tk.Canvas(master,
                                height = 150,
                                width  = 900 ,
                                bg=GB.BGColorLight, 
                                borderwidth=0,
                                highlightthickness=0)

        self.mainCanvas.grid(columnspan=3, sticky= "nsew")
        
        tk.Grid.columnconfigure(master, (0,1,2) , weight = 1)
        tk.Grid.rowconfigure(master, 7, weight = 1)

        self.LBSLogo = Image.open(util.resourcePath('images\\UI\\LB_Search.png'))
        self.LBSLogoResized = self.LBSLogo.resize(( 500, 122 ))
        self.LBSLogo = ImageTk.PhotoImage(image= self.LBSLogoResized)

        self.LBSLabel = tk.Label(image= self.LBSLogo, bg= GB.BGColorLight)
        self.LBSLabel.image = self.LBSLogo
        self.LBSLabel.grid(column=1, row=0)
        
        # ____ 
        settingsImage = tk.PhotoImage(file=util.resourcePath("images\\UI\\settings.png"))
        self.settingsButton = util.makeButton(buttonColor = GB.BGColorDark, 
                                              activeColor = GB.BGColorDark,
                                              image       = settingsImage,
                                              command     = self.openSettings)
        
        self.settingsButton.configure(height = 28, width = 120)
        self.settingsButton.grid(columnspan=3, column=0, row=1, pady=10, padx= (0,130))
        
        # ____ 
        
        self.errorImage = tk.PhotoImage(file=util.resourcePath("images/UI/error.png"))
        self.errorLabel = tk.Label(bg= GB.BGColorDark)
        self.errorLabel.grid(column=1, row=1, pady=(0,0), padx=(0, 300))
        self.errorHover = Hovertip(self.errorLabel, "", 100)
        
        # ____
        
        heartedImage = tk.PhotoImage(file=util.resourcePath("images\\UI\\hearted.png"))
        self.SavedLevelsButton = util.makeButton(buttonColor = GB.BGColorDark, 
                                                 activeColor = GB.BGColorDark,
                                                 image       = heartedImage,
                                                 command     = self.openSavedLevels)
        
        self.SavedLevelsButton.configure(height = 28, width = 120)
        self.SavedLevelsButton.grid(columnspan=3, column=0, row=1, pady=10, padx= (130,0))
        # ____ 
        
        searchLabel = tk.Label(text  = "The Search will look for level name, creator ID or any keyword in the level Description",
                               bg    = GB.BGColorDark,
                               fg    = "White",
                               font  = ('Helvatical bold',10))
        searchLabel.grid(columnspan=3, column=0, row=2)
        
        searchTextField = tk.Entry(bd= 0, font=15, bg="black", fg="white")
        searchTextField.grid(columnspan=3, row=3, column=0, ipadx= 250)

        searchBtnImage = tk.PhotoImage(file=util.resourcePath("images/UI/search.png"))
        searchButton = util.makeButton(buttonColor = GB.BGColorDark,
                                       activeColor = GB.BGColorDark,
                                       image       = searchBtnImage,
                                       command = lambda: threading.Thread(target = self.LBSsearch, 
                                                                          args   = (searchTextField.get(), 
                                                                                    self.options.archivePath)).start())
        searchButton.configure(height = 28, width = 120)
        searchButton.grid(column=1, row=4, pady=(13,13))
        
        # ____ 
        
        randomizerBtnImage = tk.PhotoImage(file=util.resourcePath("images/UI/randomizer.png"))
        randomizerButton = util.makeButton(buttonColor = GB.BGColorDark,
                                           activeColor = GB.BGColorDark,
                                           image       = randomizerBtnImage, 
                                           command      = lambda: self.fetchRandomLevels())
        randomizerButton.configure(height = 32, width = 32)
        randomizerButton.grid(column=1, row=4, pady=(13,13), padx=(0, 170))
        
        #--- Pagination
        
        self.pageLeft     = util.makeButton(text="<",  command= self.nextLeftPage)
        self.pageFarLeft  = util.makeButton(text="<<", command= self.farLeftPage)        
        self.pageRight    = util.makeButton(text=">",  command= self.nextRightPage)
        self.pageFarRight = util.makeButton(text=">>", command= self.farRightPage)
        
        # _________
        self.pageNumText  = tk.StringVar()
        self.pageNumbers = util.makeLabel(self.pageNumText)
        
        self.levelCounterTxt  = tk.StringVar()
        self.levelCounter     = util.makeLabel(self.levelCounterTxt)
        #____________________________
        
        self.globeGif = tk.Label(bg= GB.BGColorDark)
        self.globeGif.grid(column=1, row=4, padx= (185, 0) ,pady=(0,0))
        self.options.fetchSettings()
        
        
        self.dragId = ''
        master.bind('<Configure>', self.dragging)
        #___________________________________
        
    def dragging(self, event):
        if event.widget is root: 
            if self.dragId != '':
                self.master.after_cancel(self.dragId)
            # schedule resetDrag
            self.dragId = root.after(100, self.resetDrag)
            
    def resetDrag(self):
        self.dragId = '' 
            
    # search method _____________________________________________________________________________________________________________________________________
    
    def animateGlobe(self, frameNumber = 0):
        if self.isSearching == False:
            self.globeGif.config(image="")# remove the image
            return

        if frameNumber == 32: # Loops the animation when it hits the last frame.
            frameNumber = 0
        
        try:
            self.globeGif.config(image=self.globeFrames[frameNumber]) 
            self.master.after(50, self.animateGlobe, frameNumber+1)
        except:
            pass
    
    
    def startWaiter(self):
        if self.isSearching == True and self.isFirstRun == True:
            self.sendError("First run takes longer time")
            return
        
        elif self.isFirstRun == True:
            threading.Timer(10.0, self.startWaiter).start()
    
    def fetchRandomLevels(self):
        '''Fetches 50 random levels'''
        self.clearNotification()
        if self.randomLevelsPool == []:
            self.generateRandomPool = True
            threading.Thread(target = self.LBSsearch, args = ("", self.options.archivePath)).start()
            self.animateGlobe()
        else:
            
            poolPopulation = len(self.randomLevelsPool) if len(self.randomLevelsPool) < 50 else 50
            random50 = random.sample(self.randomLevelsPool, poolPopulation)
            self.showResult(random50)
            self.updatePagination(levelList= random50, random= True)
            

    
    def guardSearch(self):
        if self.isSearching: return
        if self.options.RPCS3Path.__contains__("/") == False:
            self.sendError("Please select a destination folder")
            return
        
    def LBSsearch(self, term, path):
        self.guardSearch()
        self.clearNotification()
        self.startWaiter()
        self.currentPage = 0
        self.isSearching = True
        self.animateGlobe()
        
        # this event will be called from background thread to use the main thread.
        self.master.bind("<<event1>>", self.updateSearchResult)
        self.master.bind("<<event2>>", self.updateRandom)
        self.levelParser.search(self.searchCallBack, path, term, includeDescription= self.options.includeDescription)
    
    def searchCallBack(self, response):
        self.isSearching = False
        if self.guard(response):
            return
        
        if self.generateRandomPool == False:
            levels = response if self.options.includeDups == True else set(response)                
            self.matchedLevels = util.splitLevelsToLists(levels = levels) if len(levels) > 50 else levels
        else:
            self.randomLevelsPool = response
            
        self.showPagingButtons()
        # Calls showResult on the main thread.
        self.master.event_generate("<<event1>>")
        self.master.event_generate("<<event2>>")
        
    def guard(self, response):
        self.isFirstRun = False
        if self.options.heartedLevelPaths == None:
            self.sendError("An error occurred when tried to open one of the saved paths."+ "\n"+ "Try selecting paths again.")
            return True
        
        if response == ParserReturns.noResult:
            self.sendError("No result")
            return True

        elif response == ParserReturns.noPath:
            self.sendError("Please select a levels directory from the settings")
            return True
        
        elif response == ParserReturns.wrongPath:
            self.sendError("Can't find any level archive directory")
            return True    
        
        return False
        
    # Hearted levels _______________________________________________________________________________________________________________________________________
    
    def removeLevelCallBack(self, path, removedLevelFolderName):
        try: # it will check if the removed level is in the current page, if so it will update the heart image in the ui
            tuple =  [tuple for tuple in self.currentPageLevels if tuple[0] == removedLevelFolderName][0]
            levelFolderName = tuple[0]
            levelCanvas     = tuple[1]
            self.toggleLevelHeart(check        = levelFolderName is self.options.heartedLevelPaths, 
                                  levelFolder = levelFolderName, 
                                  imageCanvas = levelCanvas)
            self.clearNotification()
            return
        except: # other wise it wil just remove the level from the hearted list
            print("DEBUG: Level cell is not on the current page")
        self.options.removeHeartedLevel(removedLevelFolderName)
        
    def currentLevels(self):
        if self.hasMoreThanOnePage == False: return self.matchedLevels
        
    def openSavedLevels(self):
        if self.options.RPCS3Path == '':
            self.sendError("Please select a destination folder")
            return
        try:
            self.savedLevels.window.lift()
        except:
            self.savedLevels = SavedLevels(master     = self.master, 
                                           removeLevelCallBack = self.removeLevelCallBack,
                                           RPCS3Path  = self.options.RPCS3Path)

    # Settings ____________________________________________________________________________________________________________________________________________
    
    def errorCallback(self, errorText):
        self.sendError(errorText)
        
    def openSettings(self):
        self.options.openSettings(master= self.master)
                        
    # Level Helpers _______________________________________________________________________________________________________________________________________
    
    def manageLevel(self, source, levelFolder, levelImageCanvas):
        destination = self.options.RPCS3Path
        destDir = os.path.join(destination,os.path.basename(source))
        try:
            if self.moveFolder(source, destDir):
                self.toggleLevelHeart(True, levelFolder, levelImageCanvas)
            else:
                self.toggleLevelHeart(False, levelFolder, levelImageCanvas)
        except:
            self.sendError("Could not handle folder properly because it is being used by another process") 
            self.options.fetchHeatedPaths(destination)
            self.toggleLevelHeart(check = levelFolder is self.options.heartedLevelPaths, levelFolder = levelFolder, imageCanvas = levelImageCanvas)
            self.refreshLevels()  
    
    
    def toggleLevelHeart(self, check, levelFolder, imageCanvas):
        if check:
            imageCanvas.itemconfig(2, state='normal')
            self.options.addHeartedLevel(levelFolder)
        else:
            imageCanvas.itemconfig(2, state='hidden')
            try:
                self.options.removeHeartedLevel(levelFolder)
            except:
                print("DEBUG: Level is not in the hearted list")
            
    def checkIfFolderIsEmpty(self, pathToCheck):
        try:
            if len(os.listdir(pathToCheck)) == 0:
                shutil.rmtree(pathToCheck)
                print("DEBUG: removed empty file.")
        except:
            print("DEBUG: Folder is not available in destination folder, it is safe to copy it.")  
                  
    def moveFolder(self, source, destDir):
        self.checkIfFolderIsEmpty(destDir)
        if exists(destDir) == False:
            shutil.copytree(source, destDir)
            self.refreshLevels()
            return True
        else:
            shutil.rmtree(destDir)
            self.refreshLevels()
            return False
        
    def refreshLevels(self):
        # refresh Saved levels automatically
        try:
            self.savedLevels.refresh()
        except:
            print("DEBUG: Cant refresh. No window on the screen")
    
    # Curser helpers __________________________________________________________________________________________________________________________________________________
    
    def _bound_to_mousewheel(self, event):
        self.scrollerCanvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _unbound_to_mousewheel(self, event):
        self.scrollerCanvas.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(self, event):
        self.clearNotification()
        self.master.update()
        self.scrollerCanvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def sendError(self, message = ""):
        self.errorLabel.config(image =self.errorImage)
        Hovertip(self.errorLabel, message, 100)
    
    def clearNotification(self):
        '''Clear current error message shown to the user.'''
        self.errorLabel.config(image="")
        self.errorHover.unschedule()
    
    def clearMatchedLevels(self):
        self.matchedLevels = []
        
    def clearRandomLevelsPool(self):
        self.randomLevelsPool = []
    
    # Pagination __________________________________________________________________________________________________________________________________________________
    
    def nextPage(self, pageLimit, moveNear = None, moveFar = None):
        if self.hasMoreThanOnePage == False     : return
        if self.currentPage        == pageLimit : return
        
        if moveNear != None: self.currentPage += moveNear
        if moveFar  != None: self.currentPage = moveFar
        self.updateSearchResult(evt="")
    
    def nextRightPage(self):
        self.nextPage(moveNear  = 1, 
                      pageLimit = len(self.matchedLevels) - 1)
        
    def nextLeftPage(self):
        self.nextPage(moveNear  =-1,
                      pageLimit = 0)
        
    def farRightPage(self):
        self.nextPage(moveFar   = len(self.matchedLevels) -1,
                      pageLimit = len(self.matchedLevels) -1)
    
    def farLeftPage(self):
        self.nextPage(moveFar   = 0,
                      pageLimit = 0)
        
    
    def updatePagination(self, levelList, random = False):
        try: # if there is a 2D list
            levelsCount = sum(len(levels) for levels in levelList)
            self.pageNumText.set(f'{self.currentPage + 1} of {len(levelList)}')
            self.hasMoreThanOnePage = True
        except: # else if there's only one list
            levelsCount = len(levelList)
            self.pageNumText.set('1')
            self.hasMoreThanOnePage = False
            
        levelsFound = "Levels" if levelsCount > 1 else "Level"
        if random:
            self.levelCounterTxt.set(f'Random {levelsCount} {levelsFound}')
        else:
            self.levelCounterTxt.set(f'{levelsCount} {levelsFound}')
    
    def updateRandom(self, evt):
        if self.generateRandomPool == False: return
        self.generateRandomPool = False
        self.fetchRandomLevels()
        self.clearMatchedLevels()

    def updateSearchResult(self, evt):
        if self.generateRandomPool == True: return
        
        self.updatePagination(levelList=self.matchedLevels)
        self.currentPageLevels = []
        matchedLevelsWithPage = self.matchedLevels[self.currentPage] if self.hasMoreThanOnePage == True else self.matchedLevels
        self.showResult(levels = matchedLevelsWithPage, isAfterSearch= False)
    
    def showPagingButtons(self):
        
        self.pageLeft.grid(column=1, row=5, ipadx=15, pady=(0, 0), padx= (0, 160))
        self.pageFarLeft.grid(column=1, row=5, ipadx=10, pady=(0, 0), padx= (0, 270))
        
        self.pageRight.grid(column=1, row=5, ipadx=15, pady=(0, 0), padx= (160, 0))
        self.pageFarRight.grid(column=1, row=5, ipadx=10, pady=(0, 0), padx= (270, 0))

        self.levelCounter.grid(column=1, row=5, ipadx=10, pady=(0, 0), padx= (470, 0))
        self.pageNumbers.grid(column=1, row=5, ipadx=20, pady=(0, 0))
        
   # builds result scroller view _______________________________________________________________________________________________________________________________
    
    def guardResult(self):
        '''Guards the app UI from being moved while refreshing the search result'''
        guarded = False
        if self.dragId != "":
            self.master.overrideredirect(True)
            guarded = True
        return guarded
    
    def createScrollerUI(self):
        '''Creates a new scrolling UI to build level cells on top'''
        scrollerBase = util.makeFrame(self.master)
        scrollerBase.grid(columnspan=3, sticky="nsew")
        
        self.scrollerCanvas = util.makeScrollerCanvas(master= scrollerBase, height= 600, width= 800)
        self.scrollerCanvas.grid(row=0, column=0, sticky= "ns")
        
        scrollBar = ttk.Scrollbar(scrollerBase, orient=VERTICAL, command=self.scrollerCanvas.yview)
        scrollBar.grid(row=0, column=3, sticky='ns')
        
        util.addScrollbarTo(canvas= self.scrollerCanvas, 
                            scrollBar= scrollBar, 
                            boundToMouseWheel = self._bound_to_mousewheel, 
                            unboundToMouseWheel = self._unbound_to_mousewheel)
            
        scrollerFrame = Canvas(self.scrollerCanvas, 
                               background          = GB.BGColorDark,
                               highlightbackground = GB.BGColorDark,
                               highlightcolor      = GB.BGColorDark)
        
        return (scrollerFrame, scrollerBase)
        
    def showResult(self,levels, isAfterSearch: bool= True):        
        self.scrollerBase.destroy()    
        newScrollerUI = self.createScrollerUI()
        
        scrollerFrame = newScrollerUI[GB.SCROLLER_FRAME]
        self.scrollerBase = newScrollerUI[GB.SCROLLER_BASE]
        
        refreshWindow = self.guardResult()
        
        scrollerFrame.grid(columnspan=3, sticky= "nsew")
        self.scrollerCanvas.create_window((0,0), window=scrollerFrame, anchor="nw")
        
        # Loop and build level cells for the scrollable frame
        for index, level in enumerate(levels):
            
            labelText = util.addBreakLine(text= level.title, strIndex= "by")         
            
            levelImageCanvas = Canvas(scrollerFrame, height=100, width=125, bg= GB.BGColorDark, bd=0, highlightthickness = 0)
            levelImageCanvas.grid(row = index, column=0)
            
            levelImage = util.resize(level.image)
            
            levelImageCanvas.create_image(55, 50, image = levelImage)
            levelImageCell = tk.Label(scrollerFrame, image=levelImage, bg=GB.BGColorDark)
            levelImageCell.image = levelImage
            
            levelImageCanvas.create_image(25, 60, image = self.levelHeart)
            
            heartState = "normal" if level.folderName in self.options.heartedLevelPaths else "hidden"
            levelImageCanvas.itemconfig(2, state=heartState) # the number 2 item is the heart png.
            
            self.currentPageLevels.append((level.folderName, levelImageCanvas))
            
            levelInfoButton = util.makeButton(master= scrollerFrame, text= labelText, font= util.resizeStringToFit(labelText),
                                              command= partial(self.manageLevel, level.path, level.folderName, levelImageCanvas))
            
            levelInfoButton.configure(bg= GB.BGColorDark, width= 57)
            
            levelInfoButton.grid(row = index, column=1, columnspan= 2, sticky="ew")

            levelDescription = "No description" if level.description == "" else level.description
            Hovertip(levelInfoButton, util.addBreakLines(levelDescription))
            
        if refreshWindow:
            self.master.overrideredirect(False)
            refreshWindow = False
        # reset to page one after searching
        
        if isAfterSearch:
            self.currentPage = 0
            
#___________________________________________________________________________________________________________________________________________________________
    
root   = tk.Tk()
LBSGUI = LittleBigSearchGUI(master= root)
root.mainloop()

