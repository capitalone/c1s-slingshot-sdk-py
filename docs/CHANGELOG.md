# Changelog

<!-- BELOW IS AUTOMATICALLY UPDATED BY COMMITIZEN -->
---
## v2.0.0 (2026-01-12)

### Feat

- add method for project deletion (#65)

## v1.2.2 (2026-01-07)

### Fix

- Revert "C1s slingshot sdk py internal sli 24708 3 (#64)" (#67)

## v1.2.1 (2025-12-10)
No changes. Bumping patch number to resolve filename conflict in PyPI.

## v1.2.0 (2025-12-10)

### Feat

- Update links in pyproject.toml and allow SLINGSHOT_API_URL in client (#58)
- apply project recommendation

## v1.1.0 (2025-11-17)

### Feat

- Add project reset route and make project get/list include argument optional (#55)

## v1.0.0 (2025-11-06)

### Feat

- Remove product_code and make workspaceId required for project.create, and documentation updates (#52)

## v0.7.0 (2025-10-23)

### Feat

- Add OpenAPI spec and utility scripts (#49)

## v0.6.1 (2025-10-03)

### Fix

- Correct project.urls (#46)

## v0.6.0 (2025-09-02)

### Feat

- Add workflow_dispatch for manual Github Action runs (#43)

### Fix

- Correct nesting of workflow_dispatch event (#45)
- throw exception on response is not json decodeable (#41)
- client handling and delete unused exception. (#38)
- Add missing dependency (#37)
- fixup documention errors (#36)
- fix docs deployment url (#34)

## v0.5.1 (2025-08-29)

### Fix

- throw exception on response is not json decodeable (#41)
- client handling and delete unused exception. (#38)
- Add missing dependency (#37)
- fixup documention errors (#36)
- fix docs deployment url (#34)

## v0.5.0 (2025-08-01)

### Feat

- update readme and contribution guide (#28)

### Fix

- wheel package target (#33)

## v0.4.0 (2025-07-24)

### Feat

- switch to apache 2.0 license (#7)
- better packaging (#26)

## v0.3.0 (2025-07-23)

### Feat

- fix version bump (#18)

### Fix

- build docs in ci workflow (#24)
- prune changelog and versions (#22)
- dont use actions to create the release (#21)
- tag release creation (#19)

## v0.1.0 (2025-07-22)

### Feat

- Add component testing (#15)
- Added core api wrappers around project and recommendation endpoints (#10)
- Add sphinx docs (#4)
- Create gh release on tag
- Use trusted publish option for pypi
- Changelog and release management
