import os

content = """import Vapor

public struct ExecuteRequest: Content {
    public var path: String

    public init(path: String) {
        self.path = path
    }
}
"""

with open("/Users/reeazmahmud/Desktop/Terminator_Ecosystem/Terminator-Integrator/Sources/Shared/ExecuteRequest.swift", "w") as f:
    f.write(content)
