# Security helpers (skeleton).
#
# This module will be expanded in the dedicated security phase. Design intent:
#
# - Validate all external inputs: URLs, files, request bodies.
# - Treat retrieved documents as untrusted data.
# - A document saying "ignore previous instructions" must never override
#   application/system instructions (prompt injection defense).
# - Never log secrets or sensitive personal data.
# - Return non-verbose, safe error responses.
