# Among Us Dumpy Gif Maker
#### Made by [Pixer](https://twitter.com/pixer415) and [ThatOneCalculator](https://twitter.com/that1calculator)!
<p align="left"> <a href="https://twitter.com/that1calculator" target="blank"><img src="https://img.shields.io/twitter/follow/that1calculator?logo=twitter&style=for-the-badge" alt="that1calculator"/></a>
 <a href="https://twitter.com/pixer415" target="blank"><img src="https://img.shields.io/twitter/follow/pixer415?logo=twitter&style=for-the-badge" alt="that1calculator"/></a></p>

##### Please credit this repository when you use this program!

![](https://cdn.discordapp.com/attachments/810799100940255260/847265488005758996/ezgif-5-d8fc3263de91.gif)
# Instructions

# Easiest: use the Discord bot
## CURRENTLY UNAVAILABLE: [Bot link](https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot)
## [Backup bot link](https://discord.com/api/oauth2/authorize?client_id=847646081877934130&permissions=117760&scope=bot)
#### Help command: `!!help`
#### Please note that this bot is awaiting verification from Discord, and currently has a server cap of 250 servers.

# Run as a program:
## Requirements:
- Java Runtime Environment 15 or newer
    - [All downloads](https://www.oracle.com/java/technologies/javase-jdk16-downloads.html)
    - Linux: use package manager.
    - Also works with [OpenJDK](https://adoptopenjdk.net)
- ImageMagick
    - [Windows (static)](https://download.imagemagick.org/ImageMagick/download/binaries/ImageMagick-7.0.11-13-Q16-x64-static.exe)
    - macOS: `brew install imagemagick` (needs [Homebrew](https://brew.sh/))
    - Linux: use package manager.

## Usage:
### Make sure to [download the jar](https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker/releases/download/v1.4/Among-Us-Dumpy-Gif-Maker-1.4.0-all.jar)!

### Basic usage:
Click and open the jar, select the file, and a file called "dumpy.gif" will be made in the same folder as the jar.

### CLI usage:
- `java -jar Among-Us-Dumpy-Gif-Maker-1.4.0-all.jar` for defaults
- `java -jar Among-Us-Dumpy-Gif-Maker-1.4.0-all.jar <lines>` for choosing a line number. Default is 9.
- `java -jar Among-Us-Dumpy-Gif-Maker-1.4.0-all.jar <lines> <filepath>` for choosing a line number AND a file path instead of using the file picker.
A file called "dumpy.gif" will be made in the same folder as the jar.

### From source:
*Not recommended unless you intend to modify the code!*
- Need [Gradle](https://gradle.org/)
```
git clone https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker
cd Among-Us-Dumpy-Gif-Maker
gradle wrapper
./gradlew shadowJar # .\gradelw.bat shadowJar if you're on Windows
java -jar ./build/libs/Among-Us-Dumpy-Gif-Maker-1.4.0-all.jar
```
