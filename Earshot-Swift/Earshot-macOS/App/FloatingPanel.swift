#if os(macOS)
import AppKit

class FloatingPanel: NSPanel {
    init(contentRect: NSRect) {
        super.init(
            contentRect: contentRect,
            styleMask: [.titled, .closable, .resizable, .nonactivatingPanel, .utilityWindow],
            backing: .buffered,
            defer: false
        )

        level = .floating
        isFloatingPanel = true
        collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        becomesKeyOnlyIfNeeded = false
        isOpaque = false
        backgroundColor = .clear
        isMovableByWindowBackground = true
        titlebarAppearsTransparent = true
        titleVisibility = .hidden
        minSize = NSSize(width: 340, height: 500)
    }

    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}
#endif
