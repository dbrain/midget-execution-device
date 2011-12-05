#
# midget-execution-device: a programmable QuickSilver clone
# Copyright (C) 2011 Thomas Lee

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os

import gtk

from . import NAME, VERSION
from .ui import Window, PopupMenu
from .engine import Engine
from .builtins import BUILTINS

def toggle_visible_handler(widget):
    def impl(sender, *args):
        if widget.get_visible():
            widget.hide()
        else:
            widget.show_all()
    return impl

def window_deleteevent(window):
    return toggle_visible_handler(window)

def statusicon_activate(window):
    return toggle_visible_handler(window)

def statusicon_popupmenu(menu):
    def impl(sender, button, timestamp):
        menu.popup(None, None, None, button, timestamp)
    return impl

def configure(engine):
    filename = os.path.join(os.getenv("HOME"), ".medrc")
    with open(filename, "r") as stream:
        source = stream.read()

    context = dict(BUILTINS)
    context["commands"] = engine.commands
    co = compile(source, filename, "exec")
    exec co in context

def run(engine=None):
    if engine is None:
        engine = Engine()
        configure(engine)

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

