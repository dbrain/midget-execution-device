from subprocess import check_call, STDOUT

def cmd_invoke(*args):
    def invoke(*args2):
        check_call(args + args2)
    return invoke

BUILTINS = {
    "invoke": cmd_invoke
}

