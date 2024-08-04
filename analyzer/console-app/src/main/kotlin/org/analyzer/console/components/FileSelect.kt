package org.analyzer.kotlin.console.components

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.MainRenderScope
import com.varabyte.kotter.runtime.SectionScope
import com.varabyte.kotter.runtime.Session
import com.varabyte.kotter.runtime.render.*
import java.nio.file.Path
import java.nio.file.Paths
import java.util.UUID
import kotlin.io.path.isDirectory
import kotlin.io.path.isRegularFile

class SelectFileContext(private var input: String? = null) {
  val id: String = UUID.randomUUID().toString()

  fun updateInput(scope: SectionScope) {
    input = scope.getInput(id)
  }

  fun getCurrentPath(): Path =
      input
          .let {
            if (it == null) {
              Paths.get("")!!
            } else {
              Paths.get(it)!!
            }
          }
          .let { it.toAbsolutePath() }

  fun isValidInput(): Boolean = getCurrentPath().isRegularFile()

  fun getBasePath(): Path {
    val path = getCurrentPath()

    return when {
      path.isDirectory() -> path
      else -> path.getParent()
    }
  }

  fun listFilesInBasePath(): List<String> =
      getBasePath().toFile().listFiles().map { it.toString() }.toList()

  fun closestCompletion(input: String): String? {
    val potentialFiles = listFilesInBasePath()
    val completion = Completions(*potentialFiles.toTypedArray())
    var prediction = completion.complete(input)
    return prediction
  }

  fun buildCompleter(): InputCompleter =
      object : InputCompleter {
        override fun complete(input: String): String? {
          return closestCompletion(input)
        }
      }
}

fun MainRenderScope.selectFile(context: SelectFileContext) {
  input(
      initialText = context.getCurrentPath().toString(),
      id = context.id,
      completer = context.buildCompleter())
  textLine()

  textLine("Current folder contains:")
  context.listFilesInBasePath().take(10).forEach { textLine("- $it") }
}

fun Session.loadFile(prompt: String, context: SelectFileContext) {
  var invalidInput by liveVarOf(false)
  section {
        bold {
          textLine()
          textLine(prompt)
          textLine()
        }
        if (invalidInput) {
          red { textLine("Current input is not a file !") }
        }
        selectFile(context)
      }
      .runUntilSignal {
        onInputEntered {
          context.updateInput(this@runUntilSignal)
          if (context.isValidInput()) {
            invalidInput = false
            signal()
          } else {
            invalidInput = true
          }
        }

        onInputChanged {
          context.updateInput(this@runUntilSignal)
          invalidInput = false
        }

        onKeyPressed {
          when (key) {
            Keys.ESC -> {
              signal()
            }
          }
        }
      }
}
