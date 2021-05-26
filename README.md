# Among Us Dumpy Gif Maker
#### Made by [Pixer](https://twitter.com/pixer415) and [ThatOneCalculator](https://twitter.com/that1calculator)!
##### Please credit this repository when you use this program!

![](https://media.discordapp.net/attachments/810799100940255260/847158407122780160/ezgif.com-gif-maker.gif)

# Instructions

## Easiest: use [the Discord bot](https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot)!

## Requirements:
- Java Runtime Environment
    - [All downloads](https://www.oracle.com/java/technologies/javase-jre8-downloads.html)
    - Linux: use package manager.
- ImageMagick
    - [Windows (static)](https://download.imagemagick.org/ImageMagick/download/binaries/ImageMagick-7.0.11-13-Q16-x64-static.exe)
    - macOS: `brew install imagemagick` (needs [Homebrew](https://brew.sh/))
    - Linux: use package manager.

## Usage:
### Make sure to [download the jar](https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker/releases/download/v1.0.4/Among-Us-Dumpy-Gif-Maker.jar)!

### Basic usage:
Click and open the jar, select the file, and a file called "dumpy.gif" will be made in the same folder as the jar.

### CLI usage:
- `java -jar Among-Us-Dumpy-Gif-Maker.jar` for defaults
- `java -jar Among-Us-Dumpy-Gif-Maker.jar <lines>` for choosing a line number. Default is 9.
- `java -jar Among-Us-Dumpy-Gif-Maker.jar <lines> <filepath>` for choosing a line number AND a file path instead of using the file picker.
A file called "dumpy.gif" will be made in the same folder as the jar.

### From source:
*Not recommended unless you intend to modify the code!*
```
git clone https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker && cd Among-Us-Dumpy-Gif-Maker && javac sus.java && java sus
```