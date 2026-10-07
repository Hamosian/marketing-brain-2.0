// Encode a JPEG frame sequence, plus an optional WAV soundtrack, into an H.264/AAC MP4.
//
// Usage:  swiftc -swift-version 5 -O scripts/frames_to_mp4.swift -o /tmp/frames_to_mp4
//         /tmp/frames_to_mp4 <framesDir> <fps> <out.mp4> [audio.wav]
//
// Frames are read as <framesDir>/f00000.jpg, f00001.jpg, ... until the first gap; the
// video size comes from the first frame. scripts/capture_frames.py writes exactly this
// layout and compiles and runs this file for you with --mp4.
//
// Why Swift: the team Macs have no ffmpeg, and AVFoundation ships with macOS, so this
// needs nothing installed. Found 2026-09-28 while rendering the Marketing Brain film.
import AVFoundation
import Foundation
import ImageIO

let args = CommandLine.arguments
guard args.count == 4 || args.count == 5, let fps = Int32(args[2]), fps > 0 else {
    print("usage: frames_to_mp4 <framesDir> <fps> <out.mp4> [audio.wav]"); exit(2)
}
let framesDir = args[1], outPath = args[3]
let wavPath: String? = args.count == 5 ? args[4] : nil

func framePath(_ i: Int) -> String { String(format: "%@/f%05d.jpg", framesDir, i) }
var count = 0
while FileManager.default.fileExists(atPath: framePath(count)) { count += 1 }
guard count > 0,
      let firstSrc = CGImageSourceCreateWithURL(URL(fileURLWithPath: framePath(0)) as CFURL, nil),
      let first = CGImageSourceCreateImageAtIndex(firstSrc, 0, nil) else {
    print("no frames at \(framePath(0))"); exit(3)
}
let W = first.width, H = first.height

let outURL = URL(fileURLWithPath: outPath)
try? FileManager.default.removeItem(at: outURL)
let writer = try! AVAssetWriter(outputURL: outURL, fileType: .mp4)

let vin = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: W,
    AVVideoHeightKey: H,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 12_000_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
        AVVideoMaxKeyFrameIntervalKey: Int(fps) * 2,
    ],
    AVVideoColorPropertiesKey: [
        AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
        AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
        AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2,
    ],
])
vin.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: vin, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
    kCVPixelBufferWidthKey as String: W,
    kCVPixelBufferHeightKey as String: H,
])
writer.add(vin)

var reader: AVAssetReader?
var readerOut: AVAssetReaderTrackOutput?
var ain: AVAssetWriterInput?
if let wavPath = wavPath {
    let asset = AVURLAsset(url: URL(fileURLWithPath: wavPath))
    guard let track = asset.tracks(withMediaType: .audio).first else { print("no audio track in \(wavPath)"); exit(4) }
    reader = try! AVAssetReader(asset: asset)
    readerOut = AVAssetReaderTrackOutput(track: track, outputSettings: [AVFormatIDKey: kAudioFormatLinearPCM])
    reader!.add(readerOut!)
    ain = AVAssetWriterInput(mediaType: .audio, outputSettings: [
        AVFormatIDKey: kAudioFormatMPEG4AAC,
        AVSampleRateKey: 44100,
        AVNumberOfChannelsKey: 2,
        AVEncoderBitRateKey: 192_000,
    ])
    ain!.expectsMediaDataInRealTime = false
    writer.add(ain!)
    guard reader!.startReading() else { print("cannot read \(wavPath): \(String(describing: reader!.error))"); exit(4) }
}

// If the writer does not start, neither input callback ever finishes and group.wait() hangs.
guard writer.startWriting() else { print("failed to start: \(String(describing: writer.error))"); exit(6) }
writer.startSession(atSourceTime: .zero)

// Video and audio are fed on their own queues: AVAssetWriter interleaves the two and stalls
// one input while the other lags, so appending all video first and then all audio can hang.
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let group = DispatchGroup()
var frame = 0
group.enter()
vin.requestMediaDataWhenReady(on: DispatchQueue(label: "video")) {
    while vin.isReadyForMoreMediaData {
        if frame >= count { vin.markAsFinished(); group.leave(); return }
        guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: framePath(frame)) as CFURL, nil),
              let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { print("unreadable frame \(frame)"); exit(5) }
        var pb: CVPixelBuffer?
        CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pb)
        let buf = pb!
        CVPixelBufferLockBaseAddress(buf, [])
        let ctx = CGContext(data: CVPixelBufferGetBaseAddress(buf), width: W, height: H, bitsPerComponent: 8,
                            bytesPerRow: CVPixelBufferGetBytesPerRow(buf), space: srgb,
                            bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue)!
        ctx.draw(img, in: CGRect(x: 0, y: 0, width: W, height: H))
        CVPixelBufferUnlockBaseAddress(buf, [])
        adaptor.append(buf, withPresentationTime: CMTime(value: CMTimeValue(frame), timescale: fps))
        frame += 1
    }
}
if let ain = ain, let readerOut = readerOut {
    group.enter()
    ain.requestMediaDataWhenReady(on: DispatchQueue(label: "audio")) {
        while ain.isReadyForMoreMediaData {
            if let sb = readerOut.copyNextSampleBuffer() { ain.append(sb); continue }
            // nil means either end of file or a read error; a read error must not pass
            // as a finished soundtrack, or the MP4 ships with the audio cut short.
            if reader?.status == .failed { print("audio read failed: \(String(describing: reader?.error))"); exit(7) }
            ain.markAsFinished(); group.leave(); return
        }
    }
}
group.wait()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed else { print("failed: \(String(describing: writer.error))"); exit(6) }

// Read the result back so the caller sees what actually landed, not what was requested.
let check = AVURLAsset(url: outURL)
let secs = CMTimeGetSeconds(check.duration)
let tracks = check.tracks.map { t -> String in
    t.mediaType == .video ? "video \(Int(t.naturalSize.width))x\(Int(t.naturalSize.height)) @\(Int(t.nominalFrameRate.rounded())) fps" : "audio"
}
let bytes = (try? FileManager.default.attributesOfItem(atPath: outPath)[.size] as? Int) ?? 0
print(String(format: "wrote %@: %.1f s, %@, %.1f MB", outPath, secs, tracks.joined(separator: " + "), Double(bytes) / 1_000_000))
