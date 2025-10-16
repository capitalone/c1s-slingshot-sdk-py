"""Validate OpenAPI Specification.

This script loads and resolces the given OpenAPI spec (following $refs) and
validates it against the OpenAPI 3.x schema. Exits with a non-zero status
if validation fails.

Usage:
    python scripts/validate_openapi.py [spec_path]

Arguments:
    spec_path: Path to the OpenAPI YAML file (default: "../docs/openapi.yaml)
"""

import sys
from collections.abc import Mapping
from typing import Any, cast

from openapi_spec_validator import validate_spec
from prance import ResolvingParser

spec_path = sys.argv[1] if len(sys.argv) > 1 else "../docs/openapi.yaml"

try:
    parser = ResolvingParser(spec_path)
    spec = parser.specification
    validate_spec(cast(Mapping[Any, Any], spec))
    print(f"✅ OpenAPI specification at {spec_path} is valid for 3.x.")
except Exception as e:
    print(f"❌ OpenAPI specification validation failed for {spec_path}: {e}")
    sys.exit(1)
