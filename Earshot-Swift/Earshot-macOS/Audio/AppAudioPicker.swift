#if os(macOS)
import ScreenCaptureKit
import SwiftUI

struct AppAudioPicker: View {
    @ObservedObject var captureManager: ScreenCaptureManager

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Picker("Audio Source", selection: $captureManager.captureAllAudio) {
                Text("All System Audio").tag(true)
                Text("Specific App").tag(false)
            }
            .pickerStyle(.segmented)

            if !captureManager.captureAllAudio {
                Picker("Application", selection: $captureManager.selectedApp) {
                    Text("Select an app...").tag(nil as SCRunningApplication?)
                    ForEach(captureManager.availableApps, id: \.bundleIdentifier) { app in
                        Text(app.applicationName).tag(app as SCRunningApplication?)
                    }
                }
            }
        }
    }
}
#endif
