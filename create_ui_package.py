import os

content = """// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "TerminatorUI",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "TerminatorUI", targets: ["TerminatorUI"]),
        .library(name: "Core", targets: ["Core"]),
        .library(name: "UIComponents", targets: ["UIComponents"]),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "Core",
            dependencies: []
        ),
        .target(
            name: "UIComponents",
            dependencies: []
        ),
        .executableTarget(
            name: "TerminatorUI",
            dependencies: ["Core", "UIComponents"]
        ),
        .testTarget(
            name: "CoreTests",
            dependencies: ["Core"]
        ),
    ]
)
"""

with open("/Users/reeazmahmud/Desktop/Terminator_Ecosystem/Terminator-UI/Package.swift", "w") as f:
    f.write(content)
