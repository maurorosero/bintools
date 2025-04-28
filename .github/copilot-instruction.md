Analyze the code changes and generate a Git commit message following these standards:

General Rules:
- Prefix the commit title with:
  - [ADDED] for new features
  - [IMPROVED] for updates or enhancements
  - [FIXED] for bug fixes
  - [REFACTORED] for code refactoring without changing functionality
  - [SOPS] for secrets management updates
  - [INIT] for initial commits
  - [DOCS] for changes to documentation, manuals, tutorials, or guides
- The commit title must be clear, imperative, and no longer than 72 characters.
- If multiple important changes exist, add a body section with bullet points.
- Always maintain a professional tone suitable for production environments.
- Do not reference issue numbers unless explicitly stated.

Special Handling by File Type:

- Shell scripts (`.sh` files):
  - Emphasize modularization through functions, proper error handling with exit codes, clear comments (including usage examples and modified dates), script versioning, and license compliance (AGPL headers).
  
- Python scripts (`.py` files):
  - Emphasize PEP-8 coding standards adherence, clear docstrings for functions and classes, robust exception handling using try-except blocks, and correct script exit codes.
  
- Node.js JavaScript files (`.js`, `.mjs`, `.cjs`) and `package.json`:
  - Highlight changes to dependencies, configuration, project scripts, and runtime behavior.
  - Emphasize best practices in asynchronous code (async/await usage), error handling (try-catch blocks), modularization, and package management updates.
  
- TypeScript files (`.ts`, `.tsx`):
  - Highlight type safety improvements (use of interfaces, types), better code structure with classes or generics, improved typing of async functions, and adherence to TypeScript best practices.
  - Mention migrations from `any` to stricter types when applicable.

- Documentation files (`.md`, `.rst`, `.txt`, or files under `/docs/`):
  - Use the [DOCS] prefix.
  - Summarize documentation improvements such as new guides, tutorials, structural reorganizations, or typo corrections.

Refactoring Notes:
- Use [REFACTORED] when the codebase is improved internally without changing external behavior.
- Examples include reorganizing code, simplifying logic, improving performance internally without altering outputs.

Additional Constraints:
- Maintain clarity and consistency aligned with MRDevs Tools Development Guide.
- Summarize what was changed in high-level terms, not how it was changed unless critical.
- Only include technical details if vital to understanding the purpose of the change.

Formatting:
- Title: single line, maximum 72 characters.
- Body: bullet points with no more than 5 bullets.
- No empty commits or generic titles allowed.
