#if os(macOS)
import SwiftUI
import EarshotKit

struct MainView: View {
    @StateObject private var viewModel = RecordingViewModel()
    @State private var showSettings = false

    var body: some View {
        VStack(spacing: 16) {
            // Waveform
            WaveformView(levels: $viewModel.audioLevels, accentColor: .accentColor)
                .padding(.horizontal)

            // Timer
            Text(viewModel.formattedTime)
                .font(.system(size: 40, weight: .light, design: .monospaced))

            // Status
            Text(viewModel.status)
                .font(.caption)
                .foregroundStyle(.secondary)
                .textCase(.uppercase)

            // Record button
            Button {
                Task { await viewModel.toggleRecording() }
            } label: {
                Text(viewModel.isRecording ? "Stop" : "Record")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.borderedProminent)
            .tint(viewModel.isRecording ? .red : .accentColor)
            .clipShape(Capsule())
            .padding(.horizontal, 40)
            .keyboardShortcut("r", modifiers: [.command, .shift])

            Divider()

            // Audio source picker
            AppAudioPicker(captureManager: viewModel.captureManager)
                .padding(.horizontal)

            Divider()

            // Transcript area
            if viewModel.isTranscribing {
                VStack(spacing: 12) {
                    ProgressView()
                        .scaleEffect(1.5)
                    Text(viewModel.status)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .frame(maxHeight: .infinity)
            } else if viewModel.segments.isEmpty {
                Text("Transcript will appear here")
                    .foregroundStyle(.tertiary)
                    .frame(maxHeight: .infinity)
            } else {
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 12) {
                        ForEach(viewModel.segments) { segment in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(formatTimestamp(segment.start) + " - " + formatTimestamp(segment.end))
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                                    .fontDesign(.monospaced)
                                Text(segment.text)
                                    .font(.body)
                                    .textSelection(.enabled)
                            }
                            .padding(.horizontal)
                        }
                    }
                    .padding(.vertical, 8)
                }
            }

            // Bottom toolbar
            HStack {
                Button {
                    showSettings = true
                } label: {
                    Image(systemName: "gear")
                }
                .buttonStyle(.plain)
                .keyboardShortcut(",", modifiers: .command)

                Spacer()

                HStack(spacing: 4) {
                    Button {
                        viewModel.currentSessionIndex = max(0, viewModel.currentSessionIndex - 1)
                    } label: {
                        Image(systemName: "chevron.left")
                    }
                    .buttonStyle(.plain)
                    .disabled(viewModel.currentSessionIndex <= 0)

                    Button {
                        viewModel.currentSessionIndex += 1
                    } label: {
                        Image(systemName: "chevron.right")
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal)
            .padding(.bottom, 8)
        }
        .padding(.top, 20)
        .frame(minWidth: 340, minHeight: 500)
        .background(.regularMaterial)
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
        .alert("Screen Recording Required", isPresented: $viewModel.showScreenRecordingAlert) {
            Button("Grant Permission") {
                // Lower our floating panel so System Settings is visible
                NSApp.windows.forEach { window in
                    if window is FloatingPanel {
                        window.level = .normal
                    }
                }
                CGRequestScreenCaptureAccess()
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Earshot needs Screen Recording permission to capture audio.\n\n1. Toggle Earshot ON in the list\n2. Click 'Quit & Reopen'\n3. Reopen the app and hit Record")
        }
        .task {
            await viewModel.captureManager.startMicMonitoringOnly()
        }
    }

    private func formatTimestamp(_ seconds: TimeInterval) -> String {
        let mins = Int(seconds) / 60
        let secs = Int(seconds) % 60
        let ms = Int((seconds.truncatingRemainder(dividingBy: 1)) * 10)
        return String(format: "%02d:%02d.%d", mins, secs, ms)
    }
}
#endif
