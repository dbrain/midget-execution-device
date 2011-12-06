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
import os

def cmd_invoke(context, args):
    pid = os.fork()
    if pid == 0:
        os.execvpe(args[0], args, os.environ)

def cmd_quit(context, args):
    gtk.main_quit()

def cmd_url(context, args):
    cmd_invoke(context, (context["engine"].settings.browser,) + args)

BUILTINS = {
    "invoke":   cmd_invoke,
    "quit":     cmd_quit,
    "url":      cmd_url
}

