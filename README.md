<p align="center">
   <a href="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands" target="blank"><img src="https://shields.io/badge/invite_the-discord_bot-7289DA?logo=discord&style=for-the-badge" height="40"/></a>
   <br><br>
   <a href="https://top.gg/bot/847164104161361921/">
      <img src="https://top.gg/api/widget/status/847164104161361921.svg" alt="Among Us Dumpy Bot" />
   </a> <a href="https://top.gg/bot/847164104161361921/">
      <img src="https://top.gg/api/widget/servers/847164104161361921.svg" alt="Among Us Dumpy Bot" />
   </a> <a href="https://top.gg/bot/847164104161361921/">
      <img src="https://top.gg/api/widget/upvotes/847164104161361921.svg" alt="Among Us Dumpy Bot" />
   </a>
   <!-- <a href="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker/">
      <img src="https://shields.io/badge/Star_on-GitHub-black?logo=github&style=flat" />
   </a> -->
   <a href="https://discord.gg/Z7UZPR3bbW/">
      <img src="https://discordapp.com/api/guilds/716364441658327120/embed.png?style=shield" alt="Discord" />
   </a>
  <h1 align="center">Among Us Dumpy Gif Maker</h1>
</p>

<h3 align="center">Made by <a href="https://t1c.dev">ThatOneCalculator</a> & <a href="https://twitter.com/pixer415">Pixer415</a></h3>
<p align="center"> <a href="https://twitter.com/that1calculator" target="blank"><img src="https://img.shields.io/twitter/follow/that1calculator?logo=twitter&style=for-the-badge" alt="that1calculator"/></a>
 <a href="https://twitter.com/pixer415" target="blank"><img src="https://img.shields.io/twitter/follow/pixer415?logo=twitter&style=for-the-badge" alt="that1calculator"/></a>
<h6 align="center"> With help from <a href="https://twitter.com/twistCMYK">twistCMYK</a>, karl-police, and auguwu!</h6>
<div align="center"> <img src="https://cdn.discordapp.com/icons/849516341933506561/a_d4c89d8bd30a116e8ea3808478f73387.gif" height=100></div>
 </p>


### Please credit this repository when you use this program!
##### Current version: 3.1.3

# Instructions

# Easiest: <a href="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands" target="blank"><img src="https://shields.io/badge/invite_the-discord_bot-7289DA?logo=discord&style=for-the-badge" height="30"/></a>
##### The help command is `!!help`.

# Run as a program:
## Requirements:
- Java Runtime Environment 15 or newer
    - [All downloads](https://www.oracle.com/java/technologies/javase-jdk16-downloads.html)
    - Also works with [OpenJDK](https://adoptopenjdk.net/releases.html?variant=openjdk16&jvmVariant=hotspot)
- ImageMagick
    - [Windows (static, v6.9.X)](https://download.imagemagick.org/ImageMagick/download/binaries/ImageMagick-6.9.12-19-Q16-x64-static.exe)
    - macOS: `brew install imagemagick` (needs [Homebrew](https://brew.sh/))
    - Linux: use package manager.

## Usage:

#### [AUR package for Arch Linux users](https://aur.archlinux.org/packages/among-us-dumpy-gif-maker/) ![arch](https://media.discordapp.net/attachments/810799100940255260/838491685892784178/ezgif-6-fd025aa8c722.png)
`yay -S among-us-dumpy-gif-maker && among-us-dumpy-gif-maker`

To everyone else:

### Make sure to [download the jar](https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker/releases/download/v3.1.3/Among-Us-Dumpy-Gif-Maker-3.1.3-all.jar)!

### Basic usage:
Click and open the jar, select the file, and a file called "dumpy.gif" will be made in the same folder as the jar.

### CLI usage:
- `java -jar Among-Us-Dumpy-Gif-Maker-3.1.3-all.jar <flags>`
All flags are optional.
Flags:
```
--background <arg>    Path to custom background
--extraoutput <arg>   Appends text to output files
--file <arg>          Path to file, hides file picker
--help                Shows this message
--lines <arg>         Changes the number of lines (defaults to 10)
--mode <arg>          Crewmade mode, currently supports default and furry
```
### From source:
*Not recommended unless you intend to modify the code!*
- Need [Gradle](https://gradle.org/)
```
git clone https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker
cd Among-Us-Dumpy-Gif-Maker
gradle wrapper
./gradlew shadowJar # .\gradelw.bat shadowJar if you're on Windows
java -jar ./build/libs/Among-Us-Dumpy-Gif-Maker-3.1.3-all.jar
```
