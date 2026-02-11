# Arcade Kiosk Maintenance — Agent/Dev Contract

## Development environment

You have access to external tools and should use them when it improves correctness and relevance:

- **Context7**: fetch up-to-date library documentation and code examples (preferred for Java, Python, LÖVE2D APIs).
- **web.run**: find general information and examples for Raspberry Pi setup, library compatibility, and deployment strategies.
- **Terminal**: test compilation, run scripts, and validate installations directly.
- **File system**: inspect game structure, configuration files, and generated documentation.

## Development rules

1. **DRY (Don''t Repeat Yourself)**: avoid duplicating logic; extract shared helpers when reuse is real.
2. **KISS (Keep It Simple)**: prefer simple, explicit code over "clever" abstractions; most functions should be
   short and focused.
3. **Language**: all identifiers, comments, and documentation must be written in French.
4. **Docstrings**: every function must have a docstring describing what it does, its input parameters, and its
   return values (use language-appropriate style: Javadoc for Java, docstrings for Python, block comments for shell scripts).
5. **Dependencies**: prefer widely used, well-maintained packages compatible with Raspberry Pi OS.
6. **Before adding a dependency**: check the official documentation, Raspberry Pi compatibility, and the date of the latest release; prefer
   libraries with clear maintenance and licensing.
7. **If a dependency is niche/risky**: justify the choice in this document and wrap it behind a small adapter
   module so it can be replaced later.
8. **No magic numbers**: avoid scattering hard-coded constants; name and centralize them in configuration files or constants classes.
9. **Centralize configuration**: behavior knobs must live in configuration files (`bouton.txt`, `description.txt`, etc.).
10. **Anti-regression**: when fixing a bug, add or update a test that would have caught it.
11. **Messages d erreur clairs**: all error messages shown to users/operators must be clear, understandable, and actionable (cause + concrete next step).

## Stack specifics

- **Platform**: Raspberry Pi 3 Model B running Raspberry Pi OS (migration from Raspbian 2017).
- **Primary language**: Java with MG2D library (custom 2D game engine).
- **Secondary languages**: Python (pygame), Lua (LÖVE2D) for some games.
- **Build tools**: Shell scripts for compilation and execution (`compilation.sh`, `lancerBorne.sh`).
- **Audio**: Java Sound API and javazoom.jl library for MP3 playback.
- **Display**: Full-screen Java graphics, custom arcade button mapping via `ClavierBorneArcade.java`.

## Source of truth

- **Game list**: Each game resides in `borne_arcade/projet/<game_name>/` with:
  - `bouton.txt`: button configuration
  - `description.txt`: game description for menu display
  - `highscore`: persistent high score storage
  - Source code (Java, Python, or Lua depending on game)
- **Main launcher**: `borne_arcade/Main.java` displays game selection menu.
- **MG2D library (canonical source)**: the only allowed source is `https://github.com/synave/MG2D`; local mirror is `MG2D/` and must stay aligned with upstream.
- **Launcher scripts**: Root-level `.sh` files launch individual games.

## Persistence

- **High scores**: Each game stores high scores in `<game_folder>/highscore` text file.
- **Configuration**: Game-specific settings in `bouton.txt` and `description.txt`.
- **System state**: Arcade kiosk boots directly to game selection menu (via `borne.desktop` autostart).

## Project constraints (must follow)

- **Documentation completeness**: ALL existing documentation must be updated whenever code changes.
- **Automated generation**: Documentation generation must be automated (technical, installation, user, game-addition guides).
- **Backward compatibility**: Migrated code must remain compatible with arcade hardware (custom buttons, display resolution).
- **Deployment automation**: After `git pull`, updates must install automatically without manual intervention.
- **Version compatibility**: Pay extreme attention to library version compatibility during migration (Java, Python, system libraries).
- **MG2D library integrity**: Do NOT modify any file under `MG2D/` (source, assets, docs, scripts). If a correction is needed, re-sync from `https://github.com/synave/MG2D` instead of editing locally. All customizations must be implemented in game code or wrapper classes.

## Quality gates

MUST maintain 100% pass rate for all quality checks:

From `borne_arcade/`:

- **Compilation**: `./compilation.sh` must succeed for all Java games.
- **Linting**: All code must follow language-specific style guides (checkstyle for Java, pylint for Python).
- **Tests**: Run automated tests for:
  - Installation script
  - Game addition procedure
  - Automated deployment
  - Individual game functionality
- **Hardware validation**: Test on physical arcade kiosk before considering work complete.
- **Documentation validation**: Verify a third party can reproduce installation from docs alone.

After each major implementation or change, run the full test suite and validate on physical hardware.

## Testing expectations

- **Unit tests** cover:
  - High score saving/loading
  - Button mapping (`ClavierBorneArcade`)
  - Game state transitions
  - Configuration file parsing
- **Integration tests** cover:
  - Game launch from main menu
  - Return to menu after game exit
  - Persistent high scores across sessions
- **System tests** cover:
  - Automated installation on fresh Raspberry Pi OS
  - Automated deployment via Git
  - Autostart on boot
  - All games functional on real hardware
- **Documentation tests** validate:
  - Installation guide completeness
  - Game addition guide accuracy
  - Technical documentation currency
