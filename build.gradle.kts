plugins {
	id("com.github.johnrengelman.shadow") version "7.0.0"
	id("org.openjfx.javafxplugin") version "0.0.10"
	application
	java
}

group = "dev.t1c.amogus"
version = "2.0.2"

repositories {
	mavenCentral()
}

javafx {
	modules("javafx.application", "javafx.event", "javafx.geometry", "javafx.scene", "javafx.stage")
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

	compileJava {
		options.encoding = "UTF-8"
	}

	build {
		dependsOn(compileJava)
		dependsOn(shadowJar)
	}
}
