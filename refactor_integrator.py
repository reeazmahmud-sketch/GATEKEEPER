import os

# Update Package.swift
package_swift_content = """// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "TerminatorIntegrator",
    platforms: [
       .macOS(.v13)
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor.git", from: "4.0.0"),
    ],
    targets: [
        .target(
            name: "Shared",
            dependencies: [
                .product(name: "Vapor", package: "vapor")
            ]
        ),
        .target(
            name: "App",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .target(name: "Shared")
            ],
            swiftSettings: [
                .unsafeFlags(["-cross-module-optimization"], .when(configuration: .release))
            ]
        ),
        .executableTarget(
            name: "Run",
            dependencies: [
                .target(name: "App")
            ]
        ),
        .executableTarget(
            name: "TerminatorUI",
            dependencies: [
                .target(name: "App"),
                .target(name: "Shared")
            ]
        ),
        .testTarget(
            name: "AppTests",
            dependencies: [
                .target(name: "App"),
                .product(name: "XCTVapor", package: "vapor"),
            ]
        )
    ]
)
"""

with open("/Users/reeazmahmud/Desktop/Terminator_Ecosystem/Terminator-Integrator/Package.swift", "w") as f:
    f.write(package_swift_content)


# Update ScriptController.swift to use Shared.ExecuteRequest
script_controller_path = "/Users/reeazmahmud/Desktop/Terminator_Ecosystem/Terminator-Integrator/Sources/App/Controllers/ScriptController.swift"
with open(script_controller_path, "r") as f:
    content = f.read()

# Replace local struct definition with import
# Note: This is a basic replace. A more robust way would be to regex out the struct.
if "struct ExecuteRequest" in content:
    # Remove the struct definition
    import re
    content = re.sub(r'struct ExecuteRequest: Content \{[^}]+\}', '', content)
    content = "import Shared\n" + content

with open(script_controller_path, "w") as f:
    f.write(content)
