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

import sys
import os
import signal
import atexit

import gtk
import gobject

from . import NAME, VERSION
from .ui import Window, PopupMenu
from .engine import Engine
from .builtins import BUILTINS

def toggle_visible(widget):
    if widget.get_visible():
        widget.hide()
    else:
        widget.present()

def toggle_visible_handler(widget):
    def impl(sender, *args):
        toggle_visible(widget)
    return impl

def window_deleteevent(window):
    return toggle_visible_handler(window)

def window_focusoutevent(window):
    def focusoutevent(sender, *args):
        if window.get_visible():
            window.hide()
    return focusoutevent

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
    context["settings"] = engine.settings
    context["commands"] = engine.commands
    co = compile(source, filename, "exec")
    exec co in context

def makesighandler(path, fd):
    def sighandler(*args):
        try:
            if fd: os.close(fd)
        finally:
            if os.path.exists(path): os.unlink(path)
        sys.exit(0)
    return sighandler

def makefifo(path, window):
    def on_fifo_data(fd, *args):
        data = os.read(fd, 8)
        toggle_visible(window)
        return True
    os.mkfifo(path, 0640)
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    gobject.io_add_watch(fd, gobject.IO_IN, on_fifo_data)

def single_instance(path, window):
    if os.path.exists(path):
        try:
            fd = os.open(path, os.O_WRONLY)
            try:
                os.write(fd, "a")
            finally:
                os.close(fd)
            sys.exit(0)
        except OSError as err:
            return makefifo(path, window)
    else:
        return makefifo(path, window)

def run(engine=None):
    if engine is None:
        engine = Engine()
        configure(engine)
    
    title = "%s v%d.%d.%d" % ((NAME,) + VERSION)

    window = Window(engine)
    fd = single_instance(engine.settings.fifo, window)
    sighandler = makesighandler(engine.settings.fifo, fd)
    signal.signal(signal.SIGQUIT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)
    window.set_title(title)
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_decorated(False)
    window.set_has_frame(False)
    window.set_keep_above(True)
    window.set_skip_taskbar_hint(False)
    window.set_skip_pager_hint(False)
    window.set_urgency_hint(True)
    window.set_focus_on_map(True)
    window.connect("delete-event", window_deleteevent(window))

    popupmenu = PopupMenu()
    popupmenu.onquit(gtk.main_quit)

    statusicon = gtk.status_icon_new_from_stock(gtk.STOCK_OPEN)
    statusicon.set_tooltip(title)
    statusicon.connect("activate", statusicon_activate(window))
    statusicon.connect("popup-menu", statusicon_popupmenu(popupmenu))

    if engine.settings.show_at_startup:
        window.show_all()
        window.present()
    statusicon.set_visible(True)

    atexit.register(sighandler)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass

