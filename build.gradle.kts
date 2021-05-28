plugins {
  id("com.github.johnrengelman.shadow") version "7.0.0"
  application
  java
}

group = "dev.t1c.amogus"
version = "1.5.1"

repositories {
   mavenCentral()
}

dependencies {
  // i have no idea if u need any but put it like:
  // implementation("...")
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
