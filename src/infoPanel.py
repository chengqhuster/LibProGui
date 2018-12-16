import wx
import wx.grid as grid
import datetime


class InfoPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour((255, 255, 255))

        font = wx.Font(wx.FontInfo(12).Family(wx.FONTFAMILY_ROMAN))
        # neighbor text
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.neighbor_text = wx.StaticText(self, label='Neighbor Table\nSnapshot : '+time, size=(100, 35),
                                           style=wx.ALIGN_CENTER_HORIZONTAL)
        self.neighbor_text.SetBackgroundColour((213, 213, 213))

        # neighbor table
        self.neighbor_table = grid.Grid(self)
        self.neighbor_table.CreateGrid(3, 3)
        self.neighbor_table.HideRowLabels()
        self.neighbor_table.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.neighbor_table.SetDefaultCellFont(font)
        # self.neighbor_table.EnableEditing(False)
        self.neighbor_table.SetColLabelValue(0, 'Mac Address')
        self.neighbor_table.SetColLabelValue(1, 'Name')
        self.neighbor_table.SetColLabelValue(2, 'Is Valid')
        self.neighbor_table.EnableDragColSize(False)

        # neighbor button
        self.neighbor_button = wx.Button(self, label='update', size=(50, 30), style=wx.BORDER_NONE)

        # cs text
        self.cs_text = wx.StaticText(self, label='Cs Table\nSnapshot : ' + time, size=(100, 35),
                                     style=wx.ALIGN_CENTER_HORIZONTAL)
        self.cs_text.SetBackgroundColour((213, 213, 213))

        # cs table
        self.cs_table = grid.Grid(self)
        self.cs_table.CreateGrid(3, 4)
        self.cs_table.HideRowLabels()
        self.cs_table.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.cs_table.SetDefaultCellFont(font)
        # self.cs_table.EnableEditing(False)
        self.cs_table.SetColLabelValue(0, 'Name')
        self.cs_table.SetColLabelValue(1, 'Sequence')
        self.cs_table.SetColLabelValue(2, 'Length')
        self.cs_table.SetColLabelValue(3, 'Is Remote')

        # cs button
        self.cs_button = wx.Button(self, label='update', size=(50, 30), style=wx.BORDER_NONE)

        # fib text
        self.fib_text = wx.StaticText(self, label='Fib Table\nSnapshot : ' + time, size=(100, 35),
                                      style=wx.ALIGN_CENTER_HORIZONTAL)
        self.fib_text.SetBackgroundColour((213, 213, 213))

        # fib table
        self.fib_table = grid.Grid(self)
        self.fib_table.CreateGrid(3, 4)
        self.fib_table.HideRowLabels()
        self.fib_table.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.fib_table.SetDefaultCellFont(font)
        self.fib_table.EnableEditing(False)
        self.fib_table.SetColLabelValue(0, 'Name')
        self.fib_table.SetColLabelValue(1, 'Length')
        self.fib_table.SetColLabelValue(2, 'Hops')
        self.fib_table.SetColLabelValue(3, 'Forward port')

        # fib button
        self.fib_button = wx.Button(self, label='update', size=(50, 30), style=wx.BORDER_NONE)

        # box sizer
        box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(box)
        box.Add(self.neighbor_text, 0, wx.EXPAND)
        horbox1 = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(horbox1, 0, wx.EXPAND)
        horbox1.Add(self.neighbor_table, 1, wx.EXPAND)
        horbox1.Add(self.neighbor_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        box.Add(self.cs_text, 0, wx.EXPAND)
        horbox2 = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(horbox2, 0, wx.EXPAND)
        horbox2.Add(self.cs_table, 1, wx.EXPAND)
        horbox2.Add(self.cs_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        box.Add(self.fib_text, 0, wx.EXPAND)
        horbox3 = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(horbox3, 0, wx.EXPAND)
        horbox3.Add(self.fib_table, 1, wx.EXPAND)
        horbox3.Add(self.fib_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)

        # event action
        self.Bind(wx.EVT_SIZE, self.ajust_table_size)
        self.neighbor_button.Bind(wx.EVT_BUTTON, self.send_req_message)
        self.cs_button.Bind(wx.EVT_BUTTON, self.send_req_message)
        self.fib_button.Bind(wx.EVT_BUTTON, self.send_req_message)

    def ajust_table_size(self, e):
        if e is not None:
            e.Skip()
        nei_table_size = self.neighbor_table.GetSize()
        self.neighbor_table.SetDefaultColSize(nei_table_size[0] / 3, True)
        self.neighbor_table.ForceRefresh()
        cs_table_size = self.cs_table.GetSize()
        self.cs_table.SetDefaultColSize(cs_table_size[0] / 4, True)
        self.cs_table.ForceRefresh()
        fib_table_size = self.fib_table.GetSize()
        self.fib_table.SetDefaultColSize(fib_table_size[0] / 4, True)
        self.fib_table.ForceRefresh()

    def send_req_message(self, e):
        button = e.GetEventObject()
        if button == self.neighbor_button:
            send = bytearray(b'\x7e\xff\x1e\x00\x34\x56\x01abcde/infom\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                             b'\x00\x00\x7e')
            self.GetParent().ser.write(send)
        elif button == self.cs_button:
            send = bytearray(b'\x7e\xff\x1e\x00\x34\x56\x01abcde/infom\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                             b'\x00\x01\x7e')
            self.GetParent().ser.write(send)
        elif button == self.fib_button:
            send = bytearray(b'\x7e\xff\x1e\x00\x34\x56\x01abcde/infom\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                             b'\x00\x02\x7e')
            self.GetParent().ser.write(send)
