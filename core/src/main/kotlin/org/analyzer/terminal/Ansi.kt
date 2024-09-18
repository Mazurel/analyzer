package org.analyzer.kotlin.terminal

public enum class ANSIStyle(val value: Int) {
  RESET(0),
  BOLD(1),
  BLACK(30),
  RED(31),
  GREEN(32),
  YELLOW(33),
  BLUE(34)
}

public enum class ANSICommand(val value: String) {
  ERASE_IN_LINE("2K")
}

public class Terminal(public val colorsEnabled: Boolean = false) {
  // TODO: Detect colors enabled based on env vars

  private val currentLine = StringBuilder()
  private val appliedStyles: MutableList<List<ANSIStyle>> = mutableListOf()
  public var inScope = false

  private val supportsColors: Boolean
    get() = this.colorsEnabled // TODO: Detect based on env

  public fun ansiStyle(command: ANSIStyle) {
    if (this.supportsColors) {
      this.currentLine.append("\u001B[${command.value}m")
    }
  }

  public fun ansiCommand(command: ANSICommand) {
    if (this.supportsColors) {
      this.currentLine.append("\u001B[${command.value}")
    }
  }

  public fun write(text: String) {
    this.currentLine.append(text)
  }

  public fun endLine() {
    this.write("\n")
    this.flush()
  }

  public fun separate() {
    this.write(" | ")
  }

  public fun flush() {
    print(this.currentLine.toString())
    this.currentLine.clear()
  }

  public fun resetStyle() {
    this.ansiStyle(ANSIStyle.RESET)
  }

  public inline fun session(scope: Terminal.() -> Unit) {
    this.scope()
    this.flush()
  }

  public fun scopedStyle(vararg styles: ANSIStyle, scope: Terminal.() -> Unit) {
    this.appliedStyles.add(listOf(*styles))

    for (style in styles) {
      this.ansiStyle(style)
    }
    this.scope()
    this.appliedStyles.dropLast(1)
    this.resetStyle()
    for (restorableStyles in this.appliedStyles) {
      for (style in restorableStyles) {
        this.ansiStyle(style)
      }
    }
  }

  public inline fun bold(crossinline scope: Terminal.() -> Unit) {
    this.scopedStyle(ANSIStyle.BOLD) { this.scope() }
  }

  public inline fun red(crossinline scope: Terminal.() -> Unit) {
    this.scopedStyle(ANSIStyle.RED) { this.scope() }
  }

  public inline fun green(crossinline scope: Terminal.() -> Unit) {
    this.scopedStyle(ANSIStyle.GREEN) { this.scope() }
  }

  public fun clearLine() {
    this.ansiCommand(ANSICommand.ERASE_IN_LINE)
    this.write("\r")
    this.flush()
  }
}
