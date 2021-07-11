plugins {
  id("com.github.johnrengelman.shadow") version "7.0.0"
  application
  java
}

group = "dev.t1c.amogus"
version = "3.1.2"

repositories {
   mavenCentral()
}

dependencies {
   implementation("commons-cli:commons-cli:1.4")
}

application {
    mainClass.set("dev.t1c.dumpy.sus")
    java {
        sourceCompatibility = JavaVersion.VERSION_15
        targetCompatibility = JavaVersion.VERSION_15
    }
}

tasks {
   compileJava {
      options.encoding = "UTF-8"
   }

   build {
      dependsOn(compileJava)
      dependsOn(shadowJar)
   }
}
