import SwiftUI

public struct WaveformView: View {
    @Binding public var levels: [Float]
    public var accentColor: Color
    public var barCount: Int

    public init(levels: Binding<[Float]>, accentColor: Color = .blue, barCount: Int = 40) {
        self._levels = levels
        self.accentColor = accentColor
        self.barCount = barCount
    }

    public var body: some View {
        GeometryReader { geometry in
            HStack(spacing: 2) {
                ForEach(0..<barCount, id: \.self) { index in
                    let level = index < levels.count ? CGFloat(levels[index]) : 0
                    RoundedRectangle(cornerRadius: 2)
                        .fill(
                            LinearGradient(
                                colors: [accentColor.opacity(0.6), accentColor],
                                startPoint: .bottom,
                                endPoint: .top
                            )
                        )
                        .frame(
                            width: max(2, (geometry.size.width - CGFloat(barCount) * 2) / CGFloat(barCount)),
                            height: max(4, geometry.size.height * level)
                        )
                        .frame(maxHeight: geometry.size.height, alignment: .bottom)
                }
            }
        }
        .frame(height: 80)
    }
}
