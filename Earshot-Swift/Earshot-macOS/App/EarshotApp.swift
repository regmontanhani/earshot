#if os(macOS)
import SwiftUI
import AppKit

@main
struct EarshotApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra("Earshot", systemImage: "waveform") {
            Button("Show Window") {
                appDelegate.showPanel()
            }
            .keyboardShortcut("e", modifiers: [.command, .shift])

            Divider()

            Button("Quit Earshot") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q")
        }
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var panel: FloatingPanel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        showPanel()
    }

    func showPanel() {
        if panel == nil {
            let panel = FloatingPanel(contentRect: NSRect(x: 0, y: 0, width: 360, height: 600))
            let hostingView = NSHostingView(rootView: MainView())
            panel.contentView = hostingView
            self.panel = panel
        }
        panel?.center()
        panel?.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
}
#endif
