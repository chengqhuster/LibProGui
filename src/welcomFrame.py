import wx
import serial
import serial.tools.list_ports
import infoFrame
import threading

import pppRecvFxn


class WelcomeFrame(wx.Frame):
    def __init__(self, parent, title, style, pos):
        wx.Frame.__init__(self, parent, title=title, style=style, pos=pos)
        self.se = serial.Serial()
        self.connectFlag = False
        self.deviceName = None
        self.macAdr = None
        self.SetBackgroundColour((255, 255, 255))
        # icon
        icon_file = '../img/icon.jpg'
        icon = wx.Icon(icon_file, wx.BITMAP_TYPE_ANY)
        self.SetIcon(icon)
        # panel & bitmap
        self.panel = wx.Panel(self)
        image_file = '../img/simplelink.jpg'
        image_bitmap = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        image_width = image_bitmap.GetWidth()
        image_height = image_bitmap.GetHeight()
        wx.StaticBitmap(self.panel, -1, image_bitmap)
        self.SetSize(image_width + 120, image_height + 40)
        # two static text
        font = wx.Font(wx.FontInfo(16).Family(wx.FONTFAMILY_ROMAN))
        self.atext = wx.StaticText(self, label='com', pos=(image_width, 50),
                                   style=wx.ALIGN_CENTRE_HORIZONTAL, size=(80, 25))
        self.atext.SetFont(font)
        self.atext.SetBackgroundColour((200, 200, 200))
        self.btext = wx.StaticText(self, label='baudrate', pos=(image_width, 180),
                                   style=wx.ALIGN_CENTRE_HORIZONTAL, size=(80, 25))
        self.btext.SetFont(font)
        self.btext.SetBackgroundColour((200, 200, 200))
        # two combo Box
        self.portlist = serial.tools.list_ports.comports()
        portnamelist = []
        for port in self.portlist:
            portnamelist.append(port[0])
        self.acombox = wx.ComboBox(self.panel, pos=(image_width, 75), size=(80, 25),
                                   choices=portnamelist, style=wx.CB_READONLY)
        self.bcombox = wx.ComboBox(self.panel, pos=(image_width, 205), size=(80, 25),
                                   choices=['256000', '128000', '115200', '57600', '56000',
                                   '38400', '19200', '14400', '9600', '4800', '2400'],
                                   style=wx.CB_READONLY)
        # start button
        self.button = wx.Button(self.panel, label="START", pos=(image_width, 320),
                                size=(80, 40), style=wx.BORDER_NONE)
        font.SetPointSize(19)
        self.button.SetFont(font)
        self.button.SetBackgroundColour((100, 200, 0))
        self.button.Bind(wx.EVT_BUTTON, self.button_click)
        # actions
        self.acombox.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.combo_up)
        self.acombox.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.combo_down)

    def combo_up(self, e):
        self.portlist = serial.tools.list_ports.comports()

    def combo_down(self, e):
        self.acombox.Clear()
        for port in self.portlist:
            self.acombox.Append(port[0])
        self.btext.Show(False)
        self.btext.Show(True)

    def button_click(self, e):
        com = self.acombox.GetStringSelection()
        if com == '':
            wx.MessageDialog(self, message='COM is not chosen', caption='ooooop...',
                             style=wx.ICON_EXCLAMATION | wx.OK).ShowModal()
            return
        baudrate = self.bcombox.GetStringSelection()
        if baudrate == '':
            wx.MessageDialog(self, message='Baudrate is not chosen', caption='ooooop...',
                             style=wx.ICON_EXCLAMATION | wx.OK).ShowModal()
            return
        rate = int(baudrate)
        self.se.baudrate = rate
        self.se.port = com
        try:
            self.se.open()
        except serial.SerialException as ex:
            wx.MessageDialog(self, message=str(ex), caption='ooooop...',
                             style=wx.ICON_EXCLAMATION | wx.OK).ShowModal()
            return
        t = threading.Thread(target=pppRecvFxn.connect_try, args=(self.se, self))
        t.setDaemon(True)
        t.start()
        t.join(3)

        # self.connectFlag = True
        # self.deviceName = b'abcde'
        # self.macAdr = b'\xff\xff\xff\xff\xff\xff'
        if not self.connectFlag:
            self.se.close()
            wx.MessageDialog(self, message='Connect to device failed', caption='ooooop...',
                             style=wx.ICON_EXCLAMATION | wx.OK).ShowModal()
            return
        self.Show(False)
        infoFrame.InfoFrame(self, title='Wireless CCN',
                            style=wx.DEFAULT_FRAME_STYLE, ser=self.se,
                            device_name=self.deviceName, mac_adr=self.macAdr)


if __name__ == '__main__':
    app = wx.App()
    frame = WelcomeFrame(None, 'Wireless CCN',
                         wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX),
                         (500, 200))
    frame.Show(True)
    app.MainLoop()
