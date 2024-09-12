package org.analyzer.kotlin.log

import org.analyzer.kotlin.log.parsers.*

class LogLine(
    public val line: String,
    public val lineNumber: Int,
    public val format: LogFormat = LogFormat.basic(),
    private val parser: LogParser? = null,
    timestampFormat: String? = null
) {
  private val formattingResult = format.matchLine(line)
  private var innerPatternID: PatternID? = null

  public val content = formattingResult.content
  public val metadata = formattingResult.fields
  public val patternID: PatternID?
    get() = innerPatternID

  public val timestamp = Timestamp(this, timestampFormat)
  public val pattern: String?
    get() =
        if (this.patternID == null) {
          null
        } else {
          parser?.humanReadable(this.patternID!!)
        }

  init {
    if (parser != null) {
      // If parser is available, use it
      innerPatternID = parser.learnLine(line)
      if (innerPatternID == null) {
        innerPatternID = parser.extractPattern(line)
      }
    }
  }

  public override fun toString(): String {
    return this.line
  }
}
