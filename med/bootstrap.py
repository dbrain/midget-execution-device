import gtk

from . import NAME, VERSION
from .ui import Window, PopupMenu

def toggle_visible_handler(widget):
    def impl(sender, *args):
        if widget.get_visible():
            widget.hide()
        else:
            widget.show()
    return impl

def window_deleteevent(window):
    return toggle_visible_handler(window)

def statusicon_activate(window):
    return toggle_visible_handler(window)

def statusicon_popupmenu(menu):
    def impl(sender, button, timestamp):
        menu.popup(None, None, None, button, timestamp)
    return impl

def run(engine):
    title = "%s v%d.%d.%d" % ((NAME,) + VERSION)

    window = Window(engine)
    window.set_title(title)
    window.set_position(gtk.WIN_POS_CENTER)
    window.connect("delete-event", window_deleteevent(window))

    popupmenu = PopupMenu()
    popupmenu.onquit(gtk.main_quit)

    statusicon = gtk.status_icon_new_from_stock(gtk.STOCK_OPEN)
    statusicon.set_tooltip(title)
    statusicon.connect("activate", statusicon_activate(window))
    statusicon.connect("popup-menu", statusicon_popupmenu(popupmenu))

    window.show_all()
    statusicon.set_visible(True)

    gtk.main()

