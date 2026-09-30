"""Re-export M9 binder tests at repo tests/ path."""

from m9_capability_binder.tests.test_binder import (  # noqa: F401
    test_high_provenance_resolves_restrict,
    test_low_provenance_cannot_resolve_isolate,
    test_native_module_optional,
    test_unknown_capability_denies,
)
