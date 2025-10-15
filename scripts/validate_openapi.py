"""Bundle (dereference) an OpenAPI specification file.

This script resolves $refs in the given OpenAPI spec and writes a single,
self-contained file suitable for publishing (e.g., to Swagger UI).

Usage:
    python scripts/bundle_openapi.py [input_path] [output_path]

Arguments:
    input_path: Path to the OpenAPI YAML file (default: "../docs/openapi.yaml")
    output_path: Path to write the bundled OpenAPI YAML file
    (default: "../docs/openapi-bundled.yaml")
"""

import sys

import yaml
from prance import ResolvingParser

input_path = sys.argv[1] if len(sys.argv) > 1 else "../docs/openapi.yaml"
output_path = sys.argv[2] if len(sys.argv) > 2 else "../docs/openapi-bundled.yaml"

parser = ResolvingParser(input_path)
spec = parser.specification

with open(output_path, "w") as f:
    yaml.dump(spec, f, sort_keys=False)

print(f"✅ Bundled OpenAPI specification written to {output_path}")
