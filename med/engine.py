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
import re

import gobject

from urllib import quote_plus as urlquote

from .builtins import BUILTINS

class Settings(object):
    def __init__(self):
        object.__init__(self)

        self.fifo = "/var/tmp/med-fifo"
        self.run_at_login = False
        self.show_at_startup = True
        self.browser = "gnome-www-browser"

class Engine(gobject.GObject):
    VAR_REGEX = re.compile(r"\${([^}]+)}")

    def __init__(self):
        gobject.GObject.__init__(self)

        self.settings = Settings()
        self.commandparser = CommandParser()
        self.commands = Commands()

    def configure(self):
        filename = os.path.join(os.getenv("HOME"), ".medrc")
        with open(filename, "r") as stream:
            source = stream.read()

        self.commands.reset()
        context = dict(BUILTINS)
        context["settings"] = self.settings
        context["commands"] = self.commands
        co = compile(source, filename, "exec")
        exec co in context

    def execute(self, command):
        args = self.commandparser.parse(command)
        cmdname, args = args[0], args[1:]
        context = {}
        context["env"] = dict(os.environ)
        context["args"] = args
        context["u"] = urlquote
        context["engine"] = self
        
        try:
            command = self.commands[cmdname]
        except KeyError:
            if cmdname.startswith("http://") or cmdname.startswith("https://"):
                BUILTINS["url"](context, (cmdname,))
                return
            elif re.match(r'^.*\.(com|org|net|us|ws|co|com\.au|org\.au|net\.au)$', cmdname.strip()):
                BUILTINS["url"](context, ("http://%s" % cmdname,))
                return
            elif cmdname.startswith("/"):
                BUILTINS["invoke"](context, ("gnome-terminal", "--working-directory=%s" % cmdname,))
                return
            else:
                raise BadCommandException("unknown command: %s" % cmdname)
        command[0](context, self.exprsubst(context, command[1]))

    def expr(self, context, arg):
        def subn_cb(match):
            try:
                return str(eval(match.group(1), context, context))
            except KeyError:
                return match.group(0)
        return self.VAR_REGEX.subn(subn_cb, arg)[0]

    def exprsubst(self, context, args):
        return tuple([self.expr(context, arg) for arg in args])

class Commands(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)

        self.reset()

    def reset(self):
        self.commands = {}
        self.emit("reset")

    def add(self, command, handler, *params):
        self.commands[command] = (handler, params)
        self.emit("add", command)

    def __getitem__(self, command):
        return self.commands[command]

    def __iter__(self):
        keys = self.commands.keys()
        keys.sort()
        return iter(keys)

gobject.signal_new("add", Commands, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [str])
gobject.signal_new("reset", Commands, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])

class BadCommandException(Exception):
    pass

class EndOfCommandException(Exception):
    pass

class UnexpectedEndOfCommandException(Exception):
    pass

class CommandParser(object):
    def __init__(self):
        object.__init__(self)

        self.command = None
        self.offset = None

    def parse(self, command):
        self.command = command
        self.offset = 0
        return [arg for arg in self]

    def __iter__(self):
        try:
            while True:
                yield self.getnext()
        except EndOfCommandException:
            pass

    def getnext(self):
        c = self.c
        n = self.n

        self.checkeoc()

        while c().isspace():
            n()

        if c() in ('"', "'"):
            return self.quoted()
        else:
            return self.simple()

    def parsewhile(self, pred, eoc, escape, skiplast):
        c = self.c
        n = self.n

        escaped = False
        temp = ""
        try:
            while pred(c(), escaped):
                if escaped:
                    if escape: temp += escape(c())
                    escaped = False
                else:
                    if c() == "\\":
                        escaped = True
                    else:
                        temp += c()
                n()
            if skiplast and not self.iseoc(): n()
        except EndOfCommandException:
            if eoc:
                eoc(temp, escaped)
            else:
                raise

        return temp

    def makesimplepred(self):
        def simple_predicate(c, escaped):
            return (not c.isspace()) or escaped
        return simple_predicate

    def simpleeoc(self, temp, escaped):
        # try to handle a "bad" escape gracefully
        if escaped: temp += "\\"

    def makesimpleescape(self):
        def simple_escape(c):
            if c.isspace() or c == "\\":
                return c
            return "\\" + c
        return simple_escape

    def simple(self):
        pred = self.makesimplepred()
        eoc = self.simpleeoc
        escape = self.makesimpleescape()
        return self.parsewhile(pred, eoc, escape, False)

    def makequotedpred(self, q):
        def quoted_predicate(c, escaped):
            return c != q or escaped
        return quoted_predicate

    def quotedeoc(self, temp, escaped):
        raise UnexpectedEndOfCommand("unterminated quote")

    def makequotedescape(self, q):
        def quoted_escape(c):
            if c == q:
                return c
            return "\\" + c
        return quoted_escape

    def quoted(self):
        q = self.c()
        self.n()

        pred = self.makequotedpred(q)
        eoc = self.quotedeoc
        escape = self.makequotedescape(q)
        return self.parsewhile(pred, eoc, escape, True)

    def c(self):
        return self.command[self.offset]

    def n(self):
        self.checkeoc()
        self.offset += 1

    def iseoc(self):
        return self.offset+1 >= len(self.command)

    def checkeoc(self):
        if self.iseoc():
            raise EndOfCommandException()

