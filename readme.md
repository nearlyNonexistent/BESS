# BESS Extends Server Systems
---

BESS is a Discord bot made for quick addition of commands via Python modules and personal hosting. Currently BESS is in prerelease Oryza -- it is not expected to be functional at all, let alone stable or have a consistent API. BESS runs on Python 3.6.1, and has not been tested on any other versions.

## Installation

Once you have the folder ready, use the dependencies file in pip to install. The unofficial Discord voice API requires extra set-up on Linux -- do whath is required.
BESS requires a config.json to work. The file exampleConfig.json has all the required keys and explanations of what they are. Eventually, it will have an interactive "installer" that provides the initial config.

## Usage

`python main.py [config file name]`. If you do not provide it with a config file name, it will default to `config.json`.

## Development

Section WIP -- check back later. Basics: add your command file to the commands folder, add it to the list of imports in the main commands file, and make it vaguely similar to the other commands.

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