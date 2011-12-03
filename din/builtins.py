def cmd_invoke(*args):
    def invoke(*args2):
        print args
    return invoke

BUILTINS = {
    "invoke": cmd_invoke
}

