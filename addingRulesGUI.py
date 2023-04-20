import wx
import json

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(600, 300))

        # созданы панель и вертикальный сайзер для добавления элементов
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        # создан горизонтальный сайзер для добавления элементов
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        # создан textbox для ввода регулярного выражения ошибки и статический текст Rule:
        st_error_key = wx.StaticText(panel, label="Rule:")
        self.txt_error_key = wx.TextCtrl(panel)
        # добавлены элементы в горизонтальный сайзер
        hbox1.Add(st_error_key, flag=wx.RIGHT, border=8)
        hbox1.Add(self.txt_error_key, proportion=1)
        # горизонтальный сайзер добавлен в вертикальный
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        # создан textbox для ввода рекомендации по ошибке и статический текст Recommendation:
        st_recom = wx.StaticText(panel, label="Recommendation:")
        self.txt_recom = wx.TextCtrl(panel)
        # создан горизонтальный сайзер для добавления элементов и добавлены элементы в горизонтальный сайзер
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(st_recom, flag=wx.RIGHT, border=8)
        hbox2.Add(self.txt_recom, proportion=1)
        # горизонтальный сайзер добавлен в вертикальный
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        # добавлен статический текст и добавлен в вертикальный сайзер
        st_window = wx.StaticText(panel, label="Список правил")
        vbox.Add(st_window, flag=wx.EXPAND | wx.ALL, border=10)
        # создан элемент для отображения файла и добавлен в вертикальный сайзер
        self.txt_window = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        vbox.Add(self.txt_window, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        # созданы кнопки
        btn_save = wx.Button(panel, label='Save')
        btn_add = wx.Button(panel, label="Add new Rule")
        # создан горизонтальный сайзер для добавления элементов и добавлены кнопки в горизонтальный сайзер
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(btn_save, flag=wx.LEFT, border=10)
        hbox3.Add(btn_add, flag=wx.LEFT, border=10)
        # горизонтальный сайзер добавлен в вертикальный
        vbox.Add(hbox3, flag=wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, border=10)
        # объявлены функции при нажатии кнопок
        self.Bind(wx.EVT_BUTTON, self.add_err_key, id=btn_add.GetId())
        self.Bind(wx.EVT_BUTTON, self.save, id=btn_save.GetId())
        # считывает файл с правилами
        with open("rules.json", "r") as f:
            self.txt_window.write(f.read())
        panel.SetSizer(vbox)

    # функция добавления правил в файл
    def add_err_key(self, event):
        new_rule = {f'{self.txt_error_key.GetValue()}': f'{self.txt_recom.GetValue()}'}
        with open("rules.json", "r+") as file:
            data = json.load(file)
            data["rules"].append(new_rule)
            file.seek(0)
            json.dump(data, file, ensure_ascii=False)
            file.close()
        self.txt_window.Clear()
        with open("rules.json", "r") as f:
            self.txt_window.write(f.read())


    # функция сохранений изменений
    def save(self, event):
        with open("rules.json", "w") as f:
            f.write(self.txt_window.GetValue())
            f.close()
        self.txt_window.Clear()
        with open("rules.json", "r") as f:
            self.txt_window.write(f.read())


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, "AddRulesGUI")
    frame.Show()
    app.MainLoop()
