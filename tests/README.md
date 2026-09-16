# AMUCS Nexus - tests

Project-wide test suites. Each directory has a purpose:

- `unit` - fast, isolated tests of single functions/modules (parsers, chunkers, utilities, retrieval functions).
- `integration` - tests that combine subsystems (API to database to retrieval to AI).
- `api` - tests of the REST API (GET, POST, validation, errors).
- `e2e` - end-to-end browser/user-flow tests.
- `security` - injection, invalid input, unauthorized access, rate limits, malicious files.
- `evaluation` - AI/retrieval quality evaluation and benchmark datasets.

No tests are written yet because little functionality exists. Tests will accompany each implemented feature.

