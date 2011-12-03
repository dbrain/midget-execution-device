class Engine(object):
    def __init__(self):
        object.__init__(self)

        self.commandparser = CommandParser()
        self.commands = Commands()

    def execute(self, command):
        args = self.commandparser.parse(command)
        self.commands[args[0]](*args[1:])

class Commands(object):
    def __init__(self):
        object.__init__(self)

        self.commands = {}

    def add(self, command, handler):
        self.commands[command] = handler

    def __getitem__(self, command):
        return self.commands[command]

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

