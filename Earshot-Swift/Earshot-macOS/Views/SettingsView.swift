#if os(macOS)
import SwiftUI

struct SettingsView: View {
    @AppStorage("modelSize") private var modelSize = "small"
    @AppStorage("alwaysOnTop") private var alwaysOnTop = true
    @AppStorage("outputDir") private var outputDir = "~/Documents/Earshot"
    @AppStorage("audioSource") private var audioSource = "system"
    @AppStorage("format_json") private var formatJSON = true
    @AppStorage("format_txt") private var formatTXT = true
    @AppStorage("format_srt") private var formatSRT = true

    @Environment(\.dismiss) var dismiss

    var body: some View {
        VStack(spacing: 0) {
            Form {
                Section("Audio & Transcription") {
                    Picker("Whisper Model", selection: $modelSize) {
                        Text("tiny").tag("tiny")
                        Text("base").tag("base")
                        Text("small").tag("small")
                        Text("medium").tag("medium")
                        Text("large-v3").tag("large-v3")
                        Text("turbo").tag("turbo")
                    }

                    Text("All transcription runs locally on your Mac")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Section("Output") {
                    HStack {
                        Text("Save Location")
                        Spacer()
                        Text(outputDir)
                            .foregroundStyle(.secondary)
                            .lineLimit(1)
                            .truncationMode(.middle)
                    }

                    Toggle("JSON", isOn: $formatJSON)
                    Toggle("TXT", isOn: $formatTXT)
                    Toggle("SRT", isOn: $formatSRT)
                }

                Section("Appearance") {
                    Toggle("Always on Top", isOn: $alwaysOnTop)
                }
            }
            .formStyle(.grouped)

            HStack {
                Spacer()
                Button("Done") {
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
            }
            .padding()
        }
        .frame(width: 420, height: 380)
    }
}
#endif
