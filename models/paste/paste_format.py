from enum import Enum


class PasteFormat(str, Enum):
    """
    Syntax highlighting formats supported by Pastebin API.
    Based on: https://pastebin.com/doc_api
    """
    # Special
    NONE = ""  # No syntax highlighting

    # Popular languages
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    GO = "go"
    RUST = "rust"
    SWIFT = "swift"
    KOTLIN = "kotlin"

    # Web technologies
    HTML5 = "html5"
    CSS = "css"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"

    # Shell/Scripting
    BASH = "bash"
    POWERSHELL = "powershell"
    LUA = "lua"
    PERL = "perl"

    # Database
    SQL = "sql"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"

    # Markup/Data
    MARKDOWN = "markdown"
    LATEX = "latex"

    # Other common formats
    TEXT = "text"
    DIFF = "diff"
    APACHE = "apache"
    NGINX = "nginx"
    DOCKER = "docker"
    MAKEFILE = "make"
    CMAKE = "cmake"

    # Assembly
    ASM = "asm"
    NASM = "nasm"

    # JVM Languages
    SCALA = "scala"
    GROOVY = "groovy"

    # Functional
    HASKELL = "haskell"
    LISP = "lisp"
    SCHEME = "scheme"

    # .NET
    VBNET = "vbnet"
    FSHARP = "fsharp"

    # Mobile
    OBJECTIVEC = "objc"

    # Other
    R = "rsplus"
    MATLAB = "matlab"
    TYPESCRIPT = "typescript"

    # Add more as needed from https://pastebin.com/doc_api
