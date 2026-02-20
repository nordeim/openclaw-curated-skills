#!/usr/bin/env swift

// EventKit bridge for creating reminders with native recurrence support
// Usage: swift eventkit-bridge.swift add --title "Meeting" --due "2026-02-10T09:00:00+09:00" --repeat weekly

import Foundation
import EventKit

// MARK: - Argument Parsing

func parseArgs(_ args: [String]) -> [String: String] {
    var result: [String: String] = [:]
    var currentKey: String? = nil

    for arg in args {
        if arg.hasPrefix("--") {
            currentKey = String(arg.dropFirst(2))
            result[currentKey!] = ""
        } else if let key = currentKey {
            result[key] = arg
            currentKey = nil
        }
    }

    return result
}

// MARK: - Date Parsing

func parseISO8601(_ dateStr: String) -> DateComponents? {
    // Format: 2026-02-10T09:00:00+09:00
    let pattern = #"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})"#
    guard let regex = try? NSRegularExpression(pattern: pattern),
          let match = regex.firstMatch(in: dateStr, range: NSRange(dateStr.startIndex..., in: dateStr)) else {
        return nil
    }

    func group(_ n: Int) -> Int? {
        guard let range = Range(match.range(at: n), in: dateStr) else { return nil }
        return Int(dateStr[range])
    }

    var components = DateComponents()
    components.year = group(1)
    components.month = group(2)
    components.day = group(3)
    components.hour = group(4)
    components.minute = group(5)
    components.second = group(6)

    return components
}

func parseEndDate(_ dateStr: String) -> EKRecurrenceEnd? {
    // Format: YYYY-MM-DD
    let pattern = #"^(\d{4})-(\d{2})-(\d{2})$"#
    guard let regex = try? NSRegularExpression(pattern: pattern),
          let match = regex.firstMatch(in: dateStr, range: NSRange(dateStr.startIndex..., in: dateStr)) else {
        return nil
    }

    func group(_ n: Int) -> Int? {
        guard let range = Range(match.range(at: n), in: dateStr) else { return nil }
        return Int(dateStr[range])
    }

    guard let year = group(1), let month = group(2), let day = group(3) else {
        return nil
    }

    var components = DateComponents()
    components.year = year
    components.month = month
    components.day = day

    guard let date = Calendar.current.date(from: components) else {
        return nil
    }

    return EKRecurrenceEnd(end: date)
}

// MARK: - Recurrence Frequency

func parseFrequency(_ freq: String) -> EKRecurrenceFrequency? {
    switch freq.lowercased() {
    case "daily": return .daily
    case "weekly": return .weekly
    case "monthly": return .monthly
    case "yearly": return .yearly
    default: return nil
    }
}

// MARK: - Main

func addReminder(args: [String: String]) {
    guard let title = args["title"], !title.isEmpty else {
        print(#"{"ok":false,"error":"--title is required"}"#)
        return
    }

    let store = EKEventStore()
    let semaphore = DispatchSemaphore(value: 0)

    store.requestFullAccessToReminders { granted, error in
        defer { semaphore.signal() }

        guard granted else {
            print(#"{"ok":false,"error":"Reminders access denied"}"#)
            return
        }

        guard let calendar = store.defaultCalendarForNewReminders() else {
            print(#"{"ok":false,"error":"No default calendar"}"#)
            return
        }

        let reminder = EKReminder(eventStore: store)
        reminder.title = title
        reminder.calendar = calendar

        // Set note if provided
        if let note = args["note"], !note.isEmpty {
            reminder.notes = note
        }

        // Set due date if provided
        if let dueStr = args["due"], !dueStr.isEmpty,
           let components = parseISO8601(dueStr) {
            reminder.dueDateComponents = components

            // Also set alarm at due time
            if let dueDate = Calendar.current.date(from: components) {
                reminder.addAlarm(EKAlarm(absoluteDate: dueDate))
            }
        }

        // Set recurrence if provided
        if let repeatStr = args["repeat"], !repeatStr.isEmpty,
           let frequency = parseFrequency(repeatStr) {

            let interval = Int(args["interval"] ?? "1") ?? 1
            var recurrenceEnd: EKRecurrenceEnd? = nil

            if let endStr = args["repeat-end"], !endStr.isEmpty {
                recurrenceEnd = parseEndDate(endStr)
            }

            let rule = EKRecurrenceRule(
                recurrenceWith: frequency,
                interval: interval,
                end: recurrenceEnd
            )
            reminder.recurrenceRules = [rule]
        }

        // Save
        do {
            try store.save(reminder, commit: true)

            let freqMap = ["daily": 0, "weekly": 1, "monthly": 2, "yearly": 3]
            let repeatVal = args["repeat"] ?? ""
            let freqNum = freqMap[repeatVal.lowercased()] ?? -1

            var result: [String: Any] = [
                "ok": true,
                "id": reminder.calendarItemIdentifier,
                "title": title
            ]

            if let due = args["due"] { result["due"] = due }
            if let note = args["note"] { result["note"] = note }
            if !repeatVal.isEmpty {
                result["repeat"] = repeatVal
                result["frequency"] = freqNum
            }
            if let interval = args["interval"] { result["interval"] = Int(interval) ?? 1 }
            if let repeatEnd = args["repeat-end"] { result["repeatEnd"] = repeatEnd }

            if let jsonData = try? JSONSerialization.data(withJSONObject: result),
               let jsonStr = String(data: jsonData, encoding: .utf8) {
                print(jsonStr)
            } else {
                print(#"{"ok":true,"id":"\#(reminder.calendarItemIdentifier)"}"#)
            }

        } catch {
            print(#"{"ok":false,"error":"\#(error.localizedDescription)"}"#)
        }
    }

    semaphore.wait()
}

func showHelp() {
    print("""
    Usage:
      swift eventkit-bridge.swift add --title "TITLE" [--due ISO_DATE] [--note "NOTE"] [--repeat daily|weekly|monthly|yearly] [--interval N] [--repeat-end YYYY-MM-DD]

    Examples:
      # Weekly recurring reminder
      swift eventkit-bridge.swift add --title "Weekly standup" --due "2026-02-10T09:00:00+09:00" --repeat weekly

      # Bi-weekly reminder until end of year
      swift eventkit-bridge.swift add --title "Review" --due "2026-02-10T14:00:00+09:00" --repeat weekly --interval 2 --repeat-end 2026-12-31
    """)
}

// MARK: - Entry Point

let args = CommandLine.arguments
let parsed = parseArgs(Array(args.dropFirst()))
let command = args.count > 1 ? args[1] : ""

switch command {
case "add":
    addReminder(args: parsed)
case "help", "--help", "-h":
    showHelp()
default:
    showHelp()
}
