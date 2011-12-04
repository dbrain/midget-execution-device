import re
from subprocess import check_call, STDOUT

VAR_REGEX = re.compile(r"\${([^}]+)}")

def var(context, arg):
    def subn_cb(match):
        try:
            return context[match.group(1)]
        except KeyError:
            return match.group(0)
    return VAR_REGEX.subn(subn_cb, arg)[0]

def varsubst(context, args):
    return tuple([var(context, arg) for arg in args])

def cmd_invoke(*args):
    def invoke(context):
        check_call(varsubst(context, args))
    return invoke

BUILTINS = {
    "invoke":   cmd_invoke,
    "varsubst": varsubst
}

