# Among Us Dumpy Gif Maker
#### Made by [Pixer](https://twitter.com/pixer415) and [ThatOneCalculator](https://twitter.com/that1calculator)!
###### With help from Telk, karl-police, and auguwu!
<p align="left"> <a href="https://twitter.com/that1calculator" target="blank"><img src="https://img.shields.io/twitter/follow/that1calculator?logo=twitter&style=for-the-badge" alt="that1calculator"/></a>
 <a href="https://twitter.com/pixer415" target="blank"><img src="https://img.shields.io/twitter/follow/pixer415?logo=twitter&style=for-the-badge" alt="that1calculator"/></a></p>

### Please credit this repository when you use this program!
##### Current version: 1.6.1

![](https://cdn.discordapp.com/attachments/810799100940255260/847265488005758996/ezgif-5-d8fc3263de91.gif)
# Instructions

# Easiest: use [the Discord bot](https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands)

# Run as a program:
## Requirements:
Java Runtime Environment 15 or newer
- [All downloads](https://www.oracle.com/java/technologies/javase-jdk16-downloads.html)
- Also works with [OpenJDK](https://adoptopenjdk.net)

## Usage:

#### [AUR package for Arch Linux users](https://aur.archlinux.org/packages/among-us-dumpy-gif-maker/) ![arch](https://media.discordapp.net/attachments/810799100940255260/838491685892784178/ezgif-6-fd025aa8c722.png)
`yay -S among-us-dumpy-gif-maker && among-us-dumpy-gif-maker`

To everyone else:

### Make sure to [download the jar](https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker/releases/download/v1.6.1/Among-Us-Dumpy-Gif-Maker-1.6.1-all.jar)!

### Basic usage:
Click and open the jar, select the file, and a file called "dumpy.gif" will be made in the same folder as the jar.

### CLI usage:
- `java -jar Among-Us-Dumpy-Gif-Maker-1.6.1-all.jar` for defaults
- `java -jar Among-Us-Dumpy-Gif-Maker-1.6.1-all.jar help/version` for help/version
- `java -jar Among-Us-Dumpy-Gif-Maker-1.6.1-all.jar lines true/false filepath` for adding arguments


#### ***All arguments optional!***
- `lines` is the number of lines, which defaults to 9.
- `true/false` is whether to dither, which generally looks better at higher resolutions but not at lower ones.
- `filepath` is a filepath to give it instead of using the file picker.

A file called "dumpy.gif" will be made in the same folder as the jar.

### From source:
*Not recommended unless you intend to modify the code!*
- Need [Gradle](https://gradle.org/)
```
git clone https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker
cd Among-Us-Dumpy-Gif-Maker
gradle wrapper
./gradlew shadowJar # .\gradelw.bat shadowJar if you're on Windows
java -jar ./build/libs/Among-Us-Dumpy-Gif-Maker-1.6.1-all.jar
```
