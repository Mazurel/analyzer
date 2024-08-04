package org.analyzer.kotlin.console.apps

import com.varabyte.kotter.runtime.Session

interface App {
  // Run self contained TUI application
  fun run(): Session.() -> Unit

  // Get the application name
  fun getAppName(): String
}
