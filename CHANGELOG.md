# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- New feature descriptions.

### Changed
- Changes made to existing features.

### Deprecated
- Deprecated features.

### Removed
- Removed features.

### Fixed
- Bug fixes.

### Security
- Security updates.

## [0.2.0] - 2024-10-18
### Added
- Added support for number field type.

### Changed
- Now undefined token env var will fallback instead of failing
- Shortened body text to 50 chars in issue string representation
- Special chars are only removed only to match Epic in issue type, instead of all single selection options
- Record scheme validation now list only missing fields.

### Fixed
- Fixed the check if a field is the schema in AirtableClient
- Fixed field type conversion problem when type can't be deduced from field name.

### Other
- Improved overall quality
- Add test commands to tasks.json.
- Add test coverage workflow.
- Add unit test workflow.
- Status badge now updated only for main branch
- Added sync to non-production sandbox
- Fixed status update in production sync workflow.
  
## [0.1.8] - 2024-10-11
### Added
- Initial release of the package.
