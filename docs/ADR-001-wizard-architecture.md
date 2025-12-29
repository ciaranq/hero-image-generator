# ADR-001: Interactive Wizard Architecture

**Date:** 2025-12-28
**Status:** Accepted
**Deciders:** Development Team
**Related:** v1.1.0 Release

## Context

Users need a more intuitive way to create hero images without memorizing CLI flags or reading documentation. The existing CLI requires specifying `--title`, `--tags`, `--year`, and `--output` for each image, which creates friction for new users and one-off image creation.

## Decision

Implement an interactive CLI wizard that:
1. Launches when running without arguments
2. Guides users through prompts step-by-step
3. Provides live preview with iterative refinement
4. Persists preferences between sessions
5. Maintains full backward compatibility with existing CLI

## Architecture

### Four-Component Modular Design

We chose a modular architecture with clear separation of concerns:

#### 1. ConfigManager
**Responsibility:** Preference persistence
**Rationale:** Isolates file I/O and platform-specific paths. Easy to test with mocked paths.

#### 2. InputPrompter
**Responsibility:** User input and validation
**Rationale:** Centralizes all input validation logic. Prevents validation code duplication across wizard.

#### 3. PreviewManager
**Responsibility:** Image preview and refinement workflow
**Rationale:** Encapsulates platform-specific preview commands. Non-fatal error handling for resilience.

#### 4. WizardRunner
**Responsibility:** Orchestration
**Rationale:** Coordinates components and manages workflow. Single entry point for wizard.

### Key Design Decisions

#### 1. No-Args Detection for Wizard Launch

**Decision:** Use `len(sys.argv) == 1` to detect wizard mode
**Alternatives Considered:**
- New flag `--wizard` (rejected: extra typing, not discoverable)
- Always show wizard menu (rejected: breaks existing workflows)

**Rationale:** Zero-friction entry. Users just run the command and get guided experience.

#### 2. Preference Persistence

**Decision:** Auto-save visual preferences (colors, fonts) to `~/.config/`
**Alternatives Considered:**
- No persistence (rejected: poor UX for repeated use)
- Save all inputs including title/tags (rejected: title/tags are content-specific)

**Rationale:** Balances convenience with sensible defaults. Visual preferences are reusable, content is not.

#### 3. Platform-Specific Preview

**Decision:** Use native preview commands per OS
**Alternatives Considered:**
- Python image viewer library (rejected: heavy dependency)
- Web-based preview (rejected: complexity)

**Rationale:** Leverages existing OS tools. No new dependencies. User's preferred viewer.

#### 4. Non-Fatal Preview Errors

**Decision:** Continue wizard if preview fails, show file path
**Alternatives Considered:**
- Fail hard on preview error (rejected: breaks wizard on headless/SSH)
- Skip preview entirely (rejected: defeats purpose)

**Rationale:** Resilience over perfection. Users can still complete workflow manually.

#### 5. Color Input Flexibility

**Decision:** Support 3 formats: `#HEX`, `HEX`, `R,G,B`
**Alternatives Considered:**
- Hex only (rejected: not user-friendly)
- RGB only (rejected: designers prefer hex)

**Rationale:** Accept multiple formats users might know. Normalize internally.

#### 6. Test-First Development

**Decision:** Write tests before implementation for all components
**Alternatives Considered:**
- Test after implementation (rejected: leads to untestable code)
- No tests (rejected: unacceptable for production)

**Rationale:** TDD ensures testable design. Caught issues early. High confidence in refactoring.

## Consequences

### Positive

- **Improved UX:** Zero learning curve for new users
- **Higher adoption:** Wizard lowers barrier to entry
- **Fewer errors:** Validation prevents invalid inputs
- **Better retention:** Saved preferences improve repeat usage
- **Maintainable:** Modular design easy to extend/modify
- **Well-tested:** 62% overall coverage, 94-100% for core modules

### Negative

- **Added complexity:** 759 lines of new code
- **More tests to maintain:** 59 new wizard tests
- **Longer CLI startup:** Imports wizard on no-args (lazy-loaded)

### Neutral

- **Backward compatibility maintained:** Existing workflows unchanged
- **New mode to support:** Wizard adds another CLI mode
- **Config file management:** Users have new config file to manage

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Preview fails on some platforms | Non-fatal errors, show file path |
| Config file corruption | Handle gracefully, use defaults |
| Keyboard interrupt during wizard | Clean exit handler |
| Tests hard to maintain | Clear test organization, mocking |
| Platform differences | Platform-specific tests, CI/CD |

## Future Enhancements

Not implemented in v1.1.0, potential for future versions:

- **Web-based preview:** Browser-based live preview
- **Batch wizard mode:** Create multiple images in one session
- **Template system:** Save/load complete image templates
- **Undo/redo:** Navigate refinement history
- **Side-by-side comparison:** Compare variations before choosing

## Lessons Learned

1. **Modular architecture pays off:** Easy to test components in isolation
2. **Platform abstraction essential:** Cross-platform support from day one
3. **Error resilience matters:** Non-fatal errors kept wizard usable
4. **TDD enforces good design:** Test-first led to cleaner interfaces
5. **User testing valuable:** Interactive testing revealed UX improvements

## References

- Implementation Plan: `docs/plans/2025-12-28-interactive-wizard.md`
- Design Document: `docs/plans/2025-12-28-interactive-wizard-design.md`
- PR: https://github.com/ciaranq/hero-image-generator/pull/1
- Release: https://github.com/ciaranq/hero-image-generator/releases/tag/v1.1.0
