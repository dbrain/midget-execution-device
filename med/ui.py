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

import gtk

from .engine import BadCommandException

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
        self.entry.connect("key-press-event", self.entry_keypress)
        self.entry.connect("activate", self.entry_activate)
        self.button = gtk.Button("Go")
        self.button.connect("clicked", self.button_clicked)

        self.connect("show", self.self_show)

        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.entry, True, True, 5)
        hbox.pack_start(self.button, False, False, 5)

        vbox = gtk.VBox(False, 0)
        vbox.pack_start(hbox, True, True, 5)

        self.add(vbox)

        self.seen_esc_press = False
        self.escape_key = gtk.gdk.keyval_from_name("Escape")

    def self_show(self, widget):
        self.get_window().focus()
        self.entry.select_region(0, -1)
        self.entry.grab_focus()

    def entry_activate(self, widget):
        self.button.activate()

    def entry_keypress(self, widget, event):
        if event.keyval == self.escape_key:
            self.seen_esc_press = True
        else:
            self.seen_esc_press = False

    def entry_keyrelease(self, widget, event):
        if event.keyval == self.escape_key and self.seen_esc_press:
            self.hide()
        self.seen_esc_press = False

    def button_clicked(self, widget):
        self.hide()
        try:
            self.engine.execute(self.entry.get_text())
        except BadCommandException as e:
            dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, e.message)
            dialog.run()
            dialog.destroy()
            self.show_all()

