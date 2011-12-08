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
import pango

from .engine import BadCommandException

TYPE_COMMAND = 1

ICONDIR = os.path.join(os.path.dirname(__file__), "..", "icon")

def get_icon_pixbuf():
    image = gtk.Image()
    image.set_from_file(os.path.join(ICONDIR, "icon.png"))
    return image.get_pixbuf()

def StatusIcon(title):
    statusicon = gtk.status_icon_new_from_pixbuf(get_icon_pixbuf())
    statusicon.set_tooltip(title)
    return statusicon

class PopupMenu(gtk.Menu):
    def __init__(self):
        gtk.Menu.__init__(self)

        self.quit_menuitem = gtk.MenuItem("_Quit")
        self.quit_menuitem.show_all()
        self.append(self.quit_menuitem)

    def onquit(self, handler):
        self.quit_menuitem.connect("activate", handler)

class Entry(gtk.Entry):
    def __init__(self, engine):
        gtk.Entry.__init__(self)

        engine.commands.connect('reset', self.commands_reset)
        engine.commands.connect('add', self.commands_add)

        self.completion = gtk.EntryCompletion()
        self.model = gtk.ListStore(str, int)
        for command in engine.commands:
            self.model.append((command, TYPE_COMMAND))
        self.completion.set_model(self.model)
        self.completion.set_text_column(0)
        self.completion.set_inline_completion(True)
        self.completion.set_inline_selection(True)
        self.completion.set_popup_completion(False)
        # self.completion.connect("action-activated", self.completion_actionactivated)

        self.set_width_chars(30)
        self.set_has_frame(False)
        border = gtk.Border()
        border.top = border.left = border.right = border.bottom = 20
        self.set_inner_border(border)
        self.set_alignment(0.5)
        self.set_icon_from_pixbuf(gtk.ENTRY_ICON_PRIMARY, get_icon_pixbuf())
        self.modify_font(pango.FontDescription("sans bold 16"))
        self.set_completion(self.completion)

    def commands_reset(self, commands):
        # TODO only remove TYPE_COMMAND items
        self.model.clear()

    def commands_add(self, commands, command):
        self.model.append((command, TYPE_COMMAND))

class Window(gtk.Window):
    def __init__(self, engine):
        gtk.Window.__init__(self)
        
        self.engine = engine

        self.set_icon(get_icon_pixbuf())

        self.set_position(gtk.WIN_POS_CENTER)
        self.set_decorated(False)
        self.set_has_frame(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(False)
        self.set_focus_on_map(True)

        self.entry = Entry(engine)
        self.entry.connect("key-release-event", self.entry_keyrelease)
        self.entry.connect("key-press-event", self.entry_keypress)
        self.entry.connect("activate", self.entry_activate)

        self.connect("show", self.self_show)

        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.entry, True, True, 5)

        vbox = gtk.VBox(False, 0)
        vbox.pack_start(hbox, True, True, 5)

        vbox.show_all()

        self.add(vbox)

        self.seen_esc_press = False
        self.escape_key = gtk.gdk.keyval_from_name("Escape")

    def self_show(self, widget):
        self.get_window().focus()
        self.entry.select_region(0, -1)
        # XXX this hack forces the window to grab keyboard focus...
        self.entry.grab_focus()

    def entry_activate(self, widget):
        self.hide()
        try:
            self.engine.execute(self.entry.get_text())
        except BadCommandException as e:
            dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, e.message)
            dialog.run()
            dialog.destroy()
            self.show_all()

    def entry_keypress(self, widget, event):
        if event.keyval == self.escape_key:
            self.seen_esc_press = True
        else:
            self.seen_esc_press = False

    def entry_keyrelease(self, widget, event):
        if event.keyval == self.escape_key and self.seen_esc_press:
            self.hide()
        self.seen_esc_press = False

