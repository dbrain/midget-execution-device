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
import socket
import struct

import gtk
import gobject

from . import NAME, VERSION
from .ui import Window, PopupMenu, StatusIcon
from .engine import Engine

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

def makesighandler(sck):
    def sighandler(*args):
        try:
            sck.close()
        except OSError:
            pass
        sys.exit(0)
    return sighandler

def startserver(host, port, window):
    def on_fifo_data(fd, *args):
        sck = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        try:
            client, addr = sck.accept()
            client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
            try:
                client.shutdown(socket.SHUT_RDWR)
            finally:
                client.close()
        except socket.error as err:
            pass
        toggle_visible(window)
        return True
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sck.bind((host, port))
    sck.listen(socket.SOMAXCONN)
    gobject.io_add_watch(sck.fileno(), gobject.IO_IN, on_fifo_data)

    sighandler = makesighandler(sck)
    signal.signal(signal.SIGQUIT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)
    atexit.register(sighandler)


def single_instance(host, port):
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
    try:
        sck.connect((host, port))
        sck.shutdown(socket.SHUT_RDWR)
        return False
    except socket.error:
        return True
    finally:
        sck.close()

def run(engine=None):
    if engine is None:
        engine = Engine()
        engine.configure()
    
    title = "%s v%d.%d.%d" % ((NAME,) + VERSION)

    if not single_instance(engine.settings.host, engine.settings.port):
        sys.exit(0)
    window = Window(engine)
    startserver(engine.settings.host, engine.settings.port, window)
    window.set_title(title)
    window.connect("delete-event", window_deleteevent(window))

    popupmenu = PopupMenu()
    popupmenu.onquit(gtk.main_quit)

    statusicon = StatusIcon(title)
    statusicon.connect("activate", statusicon_activate(window))
    statusicon.connect("popup-menu", statusicon_popupmenu(popupmenu))

    if engine.settings.show_at_startup:
        window.show_all()
        window.present()
    statusicon.set_visible(True)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass

