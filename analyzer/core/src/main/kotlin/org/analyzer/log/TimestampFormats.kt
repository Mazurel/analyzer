package org.analyzer.kotlin.log

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.DateTimeParseException
import java.time.temporal.ChronoField

private val dateFormats =
        listOf(
                // Yes, they are generated by ChatGPT :)
                "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
                "yyyyMMdd_HHmmss",
                "EEE, dd MMM yyyy HH:mm:ss z",
                "MM/dd/yyyy hh:mm a",
                "yyyy-MM-dd HH:mm:ss",
                "dd/MMM/yyyy:HH:mm:ss Z",
                "yyyyMMdd'T'HHmmssSSS",
                "EEE MMM dd HH:mm:ss zzz yyyy",
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
        )

public val dateFormatters: List<TimestampFormatter> by lazy {
    dateFormats.map { TimestampFormatter(it) }
}

class TimestampFormatter(private val pattern: String) {
    val currentYear = LocalDate.now().getYear().toLong()
    val currentMonth = LocalDate.now().getMonth().value.toLong()
    val currentDay = LocalDate.now().getDayOfYear().toLong()

    public fun parse(potentialTimestamp: String): Double? {
        var builder = DateTimeFormatterBuilder().appendPattern(pattern)

        this.tryParse(builder.toFormatter(), potentialTimestamp).let {
            if (it != null) {
                return it
            }
        }
        builder = builder.parseDefaulting(ChronoField.YEAR, this.currentYear)
        this.tryParse(builder.toFormatter(), potentialTimestamp).let {
            if (it != null) {
                return it
            }
        }
        builder = builder.parseDefaulting(ChronoField.MONTH_OF_YEAR, this.currentMonth)
        this.tryParse(builder.toFormatter(), potentialTimestamp).let {
            if (it != null) {
                return it
            }
        }
        builder = builder.parseDefaulting(ChronoField.DAY_OF_YEAR, this.currentYear)
        this.tryParse(builder.toFormatter(), potentialTimestamp).let {
            if (it != null) {
                return it
            }
        }

        return null
    }

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