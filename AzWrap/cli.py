"""
Azure Wrapper (AzWrap) CLI tool.

This module is a simplified proxy that imports and re-exports the CLI functionality
from the main module. This is to maintain backward compatibility when the package
is installed.
"""

from .main import (
    main,
    create_cli,
    create_command_function,
    load_environment,
    process_json_arg,
    Context,
    pass_context
)

if __name__ == "__main__":
    main()