from subprocess import check_call, STDOUT

def cmd_invoke(context, args):
    check_call(args)

BUILTINS = {
    "invoke":   cmd_invoke
}

