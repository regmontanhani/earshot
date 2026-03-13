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
            if viewModel.transcriptText.isEmpty {
                Text("Transcript will appear here")
                    .foregroundStyle(.tertiary)
                    .frame(maxHeight: .infinity)
            } else {
                ScrollView {
                    Text(viewModel.transcriptText)
                        .font(.body)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                        .textSelection(.enabled)
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
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
        .task {
            try? await viewModel.captureManager.refreshApps()
        }
    }
}
#endif
