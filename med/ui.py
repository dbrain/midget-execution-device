import gtk

class PopupMenu(gtk.Menu):
    def __init__(self):
        gtk.Menu.__init__(self)

        self.quit_menuitem = gtk.MenuItem("_Quit")
        self.quit_menuitem.show_all()
        self.append(self.quit_menuitem)

    def onquit(self, handler):
        self.quit_menuitem.connect("activate", handler)

class Window(gtk.Window):
    def __init__(self, engine):
        gtk.Window.__init__(self)
        
        self.engine = engine

        self.entry = gtk.Entry()
        self.entry.connect("key-release-event", self.entry_keyrelease)
        self.entry.connect("activate", self.entry_activate)
        self.button = gtk.Button("Go")
        self.button.connect("clicked", self.button_clicked)

        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(self.button, False, False, 0)

        self.add(hbox)

    def show_all(self):
        self.entry.select_region(0, -1)
        gtk.Window.show_all(self)
        self.entry.grab_focus()

    def entry_activate(self, widget):
        self.button.activate()

    def entry_keyrelease(self, widget, event):
        if event.keyval == gtk.gdk.keyval_from_name("Escape"):
            self.hide()

    def button_clicked(self, widget):
        self.engine.execute(self.entry.get_text())
        self.hide()
