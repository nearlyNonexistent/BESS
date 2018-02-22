## BESS Extends Server Systems

BESS is a Discord bot made for quick addition of commands via Python modules and personal hosting. Currently BESS is in prerelease Sorghum. Compared to Prerelease Oryza, BESS should require minimal resetting to add additional features.

## Installation

BESS can be set up in a virtualenv in the standard way. Executable requirements for BESS include ffmpeg in the path, and LibOpus (which requires extra setup on Linux systems).

BESS requires a JSON config file. An example one is provided. An installation procedure will be created that will replace the need for creating one by hand eventually.

## Usage

Run the BESS python script. Using `--help` will create a list of command line arguments. Cogs may be loaded by adding them to the JSON file's list of default cogs, or by using the `cog load` command. 

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
