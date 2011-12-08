# midget-execution-device

A programmable GTK+ QuickSilver clone for software developers.

## Status

Alpha

## Overview

[QuickSilver](http://www.blacktree.com) and [Gnome Do](http://do.davebsd.com)
are nice and all, but tools like this are just begging to be easily extensible.

[Executor](http://executor.dk/) does a great job of this on Windows, but those
of us in Gnome/GTK+ land are left wanting.

MED will address this gap.

(N.B. The name was derived from [Gnome Do](http://do.davebsd.com/):
"Gnome Do" ->  "Dwarf Executor" -> "Midget Execution Device".
I have nothing against little people. Honest.)

## Prerequisites

* Python 2.7+ (may work with as early as 2.4, but untested)
* PyGTK

## Installation

No packaging available yet, so just clone the source repository:

    git clone git://github.com/thomaslee/midget-execution-device.git

Then create a **.medrc** file in your $HOME directory:

    # /home/tom/.medrc
    
    commands.add("terminal", invoke, "gnome-terminal", "--working-directory=${args[0]}")
    commands.add("google", invoke, "chromium-browser", "http://www.google.com/?q=${u(' '.join(args))}")

Don't forget to set up a system keyboard shortcut appropriate to your
Desktop Environment to make it easier to open MED!

## Usage

Once you've created your .medrc, you can use these commands within MED.

**terminal** will open a new *gnome-terminal* window in the given directory:

    terminal /var/www

**google** will perform a Google search using the given keywords:

    google github

.medrc is a fully fledged Python script, so you can write your own actions too:

    def cmd_print(context, args):
        print args[0]

    commands.add("say", cmd_print, "${' '.join(args)}")

The "say" command will now print its arguments to the command line. Try it out!

    say hello world

## Magic

Some creep added magic to support:
**MATHEMAGIC** You can calculate basic maths using =MATHS, e.g. =123+456 (this is just evalled using python)
**Command execution** You can launch an application that is executable on your path by just typing it in, anything after it will be arguments

## License

This software is licensed under the terms of the [GPL v3 License](http://www.gnu.org/licenses/gpl-3.0.txt).

## Support

Please log defects and feature requests using the issue tracker on [github](http://github.com/thomaslee/midget-execution-device).

## About

midget-execution-device was written by [Tom Lee](http://tomlee.co).

Follow me on [Twitter](http://www.twitter.com/tglee) or
[LinkedIn](http://au.linkedin.com/pub/thomas-lee/2/386/629).

