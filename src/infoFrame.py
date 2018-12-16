import threading
import wx
import infoPanel
import topoPanel
import pppRecvFxn


class InfoFrame(wx.Frame):
    def __init__(self, parent, title, style, ser, device_name, mac_adr, pos=wx.DefaultPosition):
        wx.Frame.__init__(self, parent, title=title, style=style, pos=pos)
        self.SetBackgroundColour((155, 155, 155))
        self.SetSize((800, 500))
        self.SetMinSize((650, 200))
        self.SetPosition((420, 180))
        self.ser = ser
        self.lastChosenButton = None
        self.connectState = True
        self.devicename = device_name
        self.macadr = mac_adr

        # icon
        icon_file = '../img/icon.jpg'
        icon = wx.Icon(icon_file, wx.BITMAP_TYPE_ANY)
        self.SetIcon(icon)

        # left panel
        self.leftPanel = wx.Panel(self, size=(200, 10))
        self.leftPanel.SetBackgroundColour((200, 200, 200))
        # static and button text on left panel
        textfont = wx.Font(wx.FontInfo(12).Family(wx.FONTFAMILY_ROMAN))
        self.nameText = wx.StaticText(self.leftPanel, label='Name : {}'.format(str(self.devicename, encoding='ascii'))
                                      , size=(200, 20), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.nameText.SetFont(textfont)
        self.macText = wx.StaticText(self.leftPanel, label='Mac : {}'.format(pppRecvFxn.getmac(self.macadr)),
                                     size=(200, 20), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.macText.SetFont(textfont)
        self.conText = wx.StaticText(self.leftPanel, label='Connection Status : {}'.format(self.connectState),
                                     size=(200, 20), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.conText.SetFont(textfont)
        self.backButton = wx.Button(self.leftPanel, label="BACK",
                                    size=(80, 40), style=wx.BORDER_NONE)
        font = wx.Font(wx.FontInfo(19).Family(wx.FONTFAMILY_ROMAN))
        self.backButton.SetFont(font)
        self.backButton.SetBackgroundColour((100, 200, 0))
        # button panel(chose what to show in follow panel area)
        self.buttonPanel = wx.Panel(self, size=(100, 25))
        self.buttonPanel.SetBackgroundColour((155, 155, 155))
        # choose buttons on button panel
        button_size = (100, 25)
        self.buttonA = ChooseButton(self.buttonPanel, label='information',
                                    size=button_size, style=wx.BORDER_NONE)
        self.buttonB = ChooseButton(self.buttonPanel, label='topology',
                                    size=button_size, style=wx.BORDER_NONE)
        self.buttonC = ChooseButton(self.buttonPanel, label='transmission',
                                    size=button_size, style=wx.BORDER_NONE)
        self.buttonD = ChooseButton(self.buttonPanel, label='contrl',
                                    size=button_size, style=wx.BORDER_NONE)
        self.buttonE = ChooseButton(self.buttonPanel, label='logs',
                                    size=button_size, style=wx.BORDER_NONE)
        self.lastChosenButton = self.buttonA
        self.lastChosenButton.SetBackgroundColour((255, 255, 255))
        # blank area(static text) on button panel
        blankarea = wx.StaticText(self.buttonPanel)
        blankarea.SetBackgroundColour((232, 232, 232))
        # blank panel
        self.blankPanel = wx.Panel(self, size=(100, 5))
        self.blankPanel.SetBackgroundColour((255, 255, 255))
        # info panel & topo panel
        self.infoPanel = infoPanel.InfoPanel(self)
        self.topoPanel = topoPanel.TopoPanel(self)
        self.topoPanel.SetBackgroundColour((100, 100, 100))

        # top box sizer
        framebox = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(framebox)
        # left boxsizer
        framebox.Add(self.leftPanel, 0, wx.EXPAND | wx.ALL, 0)
        leftbox = wx.BoxSizer(wx.VERTICAL)
        self.leftPanel.SetSizer(leftbox)
        namebox = wx.BoxSizer()
        macbox = wx.BoxSizer()
        conbox = wx.BoxSizer()
        butbox = wx.BoxSizer()
        leftbox.Add(namebox, 1, wx.EXPAND)
        leftbox.Add(macbox, 1, wx.EXPAND)
        leftbox.Add(conbox, 1, wx.EXPAND)
        leftbox.Add(butbox, 1, wx.EXPAND)
        namebox.Add(self.nameText, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        macbox.Add(self.macText, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        conbox.Add(self.conText, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        butbox.Add(self.backButton, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 60)
        # right boxsizer
        rightbox = wx.BoxSizer(wx.VERTICAL)
        framebox.Add(rightbox, 1, wx.EXPAND)
        rightbox.Add(self.buttonPanel, 0, wx.EXPAND)
        rightbox.Add(self.blankPanel, 0, wx.EXPAND | (wx.ALL ^ wx.TOP), 1)
        rightbox.Add(self.infoPanel, 1, wx.EXPAND | (wx.ALL ^ wx.TOP), 1)
        rightbox.Add(self.topoPanel, 1, wx.EXPAND | (wx.ALL ^ wx.TOP), 1)
        # button panel boxsizer
        buttonpanelbox = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonPanel.SetSizer(buttonpanelbox)
        buttonpanelbox.Add(self.buttonA, 0, wx.LEFT | wx.TOP, 1)
        buttonpanelbox.Add(self.buttonB, 0, wx.ALL ^ wx.RIGHT, 1)
        buttonpanelbox.Add(self.buttonC, 0, wx.ALL ^ wx.RIGHT, 1)
        buttonpanelbox.Add(self.buttonD, 0, wx.ALL ^ wx.RIGHT, 1)
        buttonpanelbox.Add(self.buttonE, 0, wx.ALL ^ wx.RIGHT, 1)
        buttonpanelbox.Add(blankarea, 1, wx.ALL | wx.EXPAND, 1)

        # event action
        self.Bind(wx.EVT_CLOSE, self.back_to_welcome)
        self.backButton.Bind(wx.EVT_BUTTON, self.back_to_welcome)
        self.buttonA.Bind(wx.EVT_BUTTON, self.button_down)
        self.buttonB.Bind(wx.EVT_BUTTON, self.button_down)
        self.buttonC.Bind(wx.EVT_BUTTON, self.button_down)
        self.buttonD.Bind(wx.EVT_BUTTON, self.button_down)
        self.buttonE.Bind(wx.EVT_BUTTON, self.button_down)

        # show frame(get components' real size after this)
        self.topoPanel.Show(False)
        self.Show(True)
        self.infoPanel.ajust_table_size(None)

        # start recv thread
        self.t1 = threading.Thread(target=pppRecvFxn.recvfxn, name='writeThread', args=(self.ser, self))
        self.t1.start()

    def back_to_welcome(self, e):
        self.ser.close()
        self.GetParent().connectFlag = False
        self.GetParent().Show(True)
        self.Destroy()

    def button_down(self, e):
        button = e.GetEventObject()
        sizer = self.buttonPanel.GetSizer()
        button.SetBackgroundColour((255, 255, 255))
        sizer.GetItem(button).SetFlag(wx.LEFT | wx.TOP)
        if self.lastChosenButton != button:
            self.lastChosenButton.SetBackgroundColour((212, 212, 212))
            sizer.GetItem(self.lastChosenButton).SetFlag(wx.ALL ^ wx.RIGHT)
            self.lastChosenButton = button
            if button == self.buttonA:
                self.topoPanel.Show(False)
                self.infoPanel.Show(True)
                self.infoPanel.ajust_table_size(None)
            else:
                self.infoPanel.Show(False)
                self.topoPanel.Show(True)
            sizer.Layout()


class ChooseButton(wx.Button):
    def __init__(self, parent, label, size, style):
        wx.Button.__init__(self, parent=parent, label=label, size=size, style=style)
        font = wx.Font(wx.FontInfo(12).Family(wx.FONTFAMILY_ROMAN))
        self.SetForegroundColour((51, 51, 51))
        self.SetBackgroundColour((212, 212, 212))
        self.SetFont(font)
