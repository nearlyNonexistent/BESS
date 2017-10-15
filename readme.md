## BESS Extends Server Systems

BESS is a Discord bot made for quick addition of commands via Python modules and personal hosting. Currently BESS is in prerelease Oryza -- it is not expected to be functional at all, let alone stable or have a consistent API. BESS runs on Python 3.6.1, and has not been tested on any other versions.

## Installation

Once you have the folder ready, you will need to install the dependencies. These dependencies are:

* Discord\[voice\]
* python-levenshtein
* asyncio

The unofficial Discord voice API requires extra set-up on Linux -- do what is required.
BESS requires a config JSON file to work, by default it loads `config.json`. The file exampleConfig.json has all the required keys and explanations of what they are. Eventually, it will have an interactive "installer" that provides the initial config.

## Usage

`python main.py [config file name]`. If you do not provide it with a config file name, it will default to `config.json`.

## Development

Commands are stored in the folder "commands", which contains an `__init__.py` file. This file stores the `CommandHandler` and the template class for commands.

The `CommandHandler` stores the variables all commands will require, and lists all commands for BESS's main loop to access. At the time of writing, each command has one name and docstring -- with the command name being used to call the command, and the docstring as an explanation of the command that is user-facing.

The `Command` class meanwhile acts as a template for command object lists. It contains methods to mention users, parse messages for arguments, and send messages. All messages sent must use the command `__respond__`, which must be passed a message and either text or an embed. By default, respond messages do not ping. This is to comply with standard best practices -- pass a `ping=True` to force a ping.

The reason for using `__respond__` is that, by default, it prepends unicode character `\u200B` to every message. This prevents commands from triggering bots that are improperly programmed. Commands must import asyncio and discord APIs to properly function, and should `from commands import Command`. All command objects must inherit from `Command`, and consist of various function names.

Command function names *must* be unique across files, and *cannot* start with underscores (unless they are internal and not meant for user access), this is due to the horrendous current solution to listing them. Similarly, they must have docstrings. Finally, they must all take the argument `trueself` first, which is used to access configuration settings if necessary.

## License

Copyright (c) 2017 nearlyNonexistent, contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
