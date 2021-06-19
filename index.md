<link rel="shortcut icon" type="image/x-icon" href="https://cdn.discordapp.com/attachments/849523719582777367/855599737608601640/emote.gif"/>
 <link rel="stylesheet" href="style.css">
<meta name="theme-color" content="#FCE40C"/>
<meta name="description" content="Among Us Dumpy Gif Maker!">
<meta property="og:image" content="https://cdn.discordapp.com/icons/849516341933506561/a_31c9be842b1a47f2fe939a1415b75f8b.gif"/>
<meta property="twitter:image" content="https://cdn.discordapp.com/icons/849516341933506561/a_31c9be842b1a47f2fe939a1415b75f8b.gif"/>
<p align="center">
   <a href="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands" target="blank"><img src="https://shields.io/badge/invite_the-discord_bot-7289DA?logo=discord&style=for-the-badge" height="40"/></a>
   <br><br>
   <a href="https://top.gg/bot/847164104161361921/">
      <img src="https://top.gg/api/widget/status/847164104161361921.svg" alt="Among Us Dumpy Bot" />
   </a> <a href="https://top.gg/bot/847164104161361921/">
      <img src="https://top.gg/api/widget/servers/847164104161361921.svg" alt="Among Us Dumpy Bot" />
   </a> <a href="https://top.gg/bot/847164104161361921/">
      <img src="https://top.gg/api/widget/upvotes/847164104161361921.svg" alt="Among Us Dumpy Bot" />
   </a> <a href="https://discord.gg/Z7UZPR3bbW/">
      <img src="https://discordapp.com/api/guilds/716364441658327120/embed.png?style=shield" alt="Discord" />
   </a>
  <h1 align="center">Among Us Dumpy Gif Maker</h1>
</p>

<h2 align="center">Made by <a href="https://t1c.dev">ThatOneCalculator</a> & <a href="https://twitter.com/pixer415">Pixer</a></h2>
<p align="center"> <a href="https://twitter.com/that1calculator" target="blank"><img src="https://img.shields.io/twitter/follow/that1calculator?logo=twitter&style=for-the-badge" alt="that1calculator"/></a>
 <a href="https://twitter.com/pixer415" target="blank"><img src="https://img.shields.io/twitter/follow/pixer415?logo=twitter&style=for-the-badge" alt="that1calculator"/></a>
<h4 align="center"> With help from Telk, karl-police, and auguwu!</h4>
<div align="center"> <img src="https://media.discordapp.net/attachments/810799100940255260/853461754016694312/servericon.gif" height=100></div>
 </p>


### Please credit this repository when you use this program!
##### Current version: 2.0.2

# Instructions

# Easiest: <a href="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands" target="blank"><img src="https://shields.io/badge/invite_the-discord_bot-7289DA?logo=discord&style=for-the-badge" height="30"/></a>
##### The help command is `!!help`.

# Run as a program:
## Requirements:
- Java Runtime Environment 15 or newer
    - [All downloads](https://www.oracle.com/java/technologies/javase-jdk16-downloads.html)
    - Also works with [OpenJDK](https://adoptopenjdk.net/releases.html?variant=openjdk16&jvmVariant=hotspot)
- ImageMagick
    - [Windows (static)](https://download.imagemagick.org/ImageMagick/download/binaries/ImageMagick-7.0.11-13-Q16-x64-static.exe)
    - macOS: `brew install imagemagick` (needs [Homebrew](https://brew.sh/))
    - Linux: use package manager.

## Usage:

#### [AUR package for Arch Linux users](https://aur.archlinux.org/packages/among-us-dumpy-gif-maker/) ![arch](https://media.discordapp.net/attachments/810799100940255260/838491685892784178/ezgif-6-fd025aa8c722.png)
`yay -S among-us-dumpy-gif-maker && among-us-dumpy-gif-maker`

To everyone else:

### Make sure to [download the jar](https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker/releases/download/v2.0.2/Among-Us-Dumpy-Gif-Maker-2.0.2-all.jar)!

### Basic usage:
Click and open the jar, select the file, and a file called "dumpy.gif" will be made in the same folder as the jar.

### CLI usage:
- `java -jar Among-Us-Dumpy-Gif-Maker-2.0.2-all.jar` for defaults
- `java -jar Among-Us-Dumpy-Gif-Maker-2.0.2-all.jar help/version` for help/version
- `java -jar Among-Us-Dumpy-Gif-Maker-2.0.2-all.jar lines filepath` for adding arguments


#### *All arguments optional!*
- `lines` is the number of lines, which defaults to 9.
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
java -jar ./build/libs/Among-Us-Dumpy-Gif-Maker-2.0.2-all.jar
```
