package org.analyzer.kotlin.log

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.DateTimeParseException
import java.time.temporal.ChronoField
import java.util.Locale

private val dateFormats =
    listOf(
        "yyyyMMdd_HHmmss",
        "MM/dd/yyyy hh:mm a",
        "yyyy-MM-dd HH:mm:ss",
        "dd/MMM/yyyy:HH:mm:ss Z",
        "yyyy-MM-dd'T'HH:mm:ss",
        "dd-MMM-yyyy HH:mm:ss",
        "yyyy/MM/dd HH:mm:ss",
        "dd-MM-yyyy HH:mm:ss",
        "MM/dd/yyyy HH:mm:ss",
        "HH:mm:ss dd/MM/yyyy",
        "dd/MMM/yyyy",
        "yyyy/MM/dd",
        "MM-dd-yyyy",
        "dd-MM-yyyy",
        "dd.MM.yyyy",
        "MM/dd/yyyy",
        "yyyy-MM-dd",
        "MM-dd HH:mm:ss", // 03-17 16:13:38
        "MM-dd HH:mm:ss.SSS", // 03-17 16:13:38.811
        "EEE MMM dd HH:mm:ss yyyy", // Sun Dec 04 04:47:44 2005
        "MM.dd HH:mm:ss", // 10.30 16:49:06
    )

public val dateFormatters: List<TimestampFormatter> by lazy {
  dateFormats.map { TimestampFormatter(it) }
}

class TimestampFormatter(public val pattern: String) {
  val currentYear = LocalDate.now().getYear().toLong()
  val currentMonth = LocalDate.now().getMonth().value.toLong()
  val currentDay = LocalDate.now().getDayOfYear().toLong()

  val allPossibleFormats: List<DateTimeFormatter>

  init {
    val formats: MutableList<DateTimeFormatter> = mutableListOf()

    var builder = DateTimeFormatterBuilder().appendPattern(pattern)
    formats.add(builder.toFormatter(Locale.ENGLISH))
    builder =
        DateTimeFormatterBuilder()
            .append(formats.last())
            .parseDefaulting(ChronoField.YEAR, this.currentYear)
    formats.add(builder.toFormatter(Locale.ENGLISH))
    builder =
        DateTimeFormatterBuilder()
            .append(formats.last())
            .parseDefaulting(ChronoField.MONTH_OF_YEAR, this.currentMonth)
    formats.add(builder.toFormatter(Locale.ENGLISH))
    builder =
        DateTimeFormatterBuilder()
            .append(formats.last())
            .parseDefaulting(ChronoField.DAY_OF_YEAR, this.currentYear)
    formats.add(builder.toFormatter(Locale.ENGLISH))

    this.allPossibleFormats = formats
  }

  public fun parse(potentialTimestamp: String): Double? {
    this.allPossibleFormats.forEach { possibleFormat ->
      this.tryParse(possibleFormat, potentialTimestamp).let { epoch ->
        if (epoch != null) {
          return epoch
        }
      }
    }

    return null
  }

  // @Suppress("NOTHING_TO_INLINE") // This function is called a lot
  private fun tryParse(formatter: DateTimeFormatter, potentialTimestamp: String): Double? {
    try {
      return LocalDateTime.parse(potentialTimestamp, formatter)
          .toInstant(ZoneOffset.UTC)
          .getEpochSecond()
          .toDouble()
    } catch (ex: DateTimeParseException) {}

    try {
      return LocalDate.parse(potentialTimestamp, formatter).toEpochDay().toDouble()
    } catch (ex: DateTimeParseException) {}

    return null
  }
}