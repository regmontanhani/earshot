#if os(macOS)
import ScreenCaptureKit
import SwiftUI

struct AppAudioPicker: View {
    @ObservedObject var captureManager: ScreenCaptureManager
    @State private var loadingApps = false
    @State private var permissionNeeded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Picker("Audio Source", selection: $captureManager.captureAllAudio) {
                Text("All System Audio").tag(true)
                Text("Specific App").tag(false)
            }
            .pickerStyle(.segmented)

            if !captureManager.captureAllAudio {
                if permissionNeeded {
                    HStack {
                        Text("Screen Recording permission required")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Spacer()
                        Button("Open Settings") {
                            NSWorkspace.shared.open(
                                URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture")!
                            )
                        }
                        .font(.caption)
                    }
                } else if loadingApps {
                    ProgressView("Loading apps...")
                        .font(.caption)
                } else {
                    HStack {
                        Picker("Application", selection: $captureManager.selectedApp) {
                            Text("Select an app...").tag(nil as SCRunningApplication?)
                            ForEach(captureManager.availableApps, id: \.bundleIdentifier) { app in
                                Text(app.applicationName).tag(app as SCRunningApplication?)
                            }
                        }

                        Button {
                            Task { await loadApps() }
                        } label: {
                            Image(systemName: "arrow.clockwise")
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
        .onChange(of: captureManager.captureAllAudio) { _, isAll in
            if !isAll && captureManager.availableApps.isEmpty {
                Task { await loadApps() }
            }
        }
    }

    private func loadApps() async {
        loadingApps = true
        permissionNeeded = false
        let granted = await captureManager.ensureScreenRecordingAccess()
        if !granted || captureManager.availableApps.isEmpty {
            permissionNeeded = true
        }
        loadingApps = false
    }
}
#endif
