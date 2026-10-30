# Contributing to ZERO-INBOX

Thank you for your interest in contributing to PROJECT ZERO-INBOX!

## Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all contributors.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Swapnil-Biswas/Zero-Inbox.git
   cd Zero-Inbox
   ```

2. Setup backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Setup frontend:
   ```bash
   cd ../frontend
   npm install
   ```

## Running Tests

Before submitting a pull request, ensure all tests pass:
```bash
cd backend
python -m unittest discover tests

cd ../frontend
npm run build
```

## Commit Convention
We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation updates
- `test:` for test additions or modifications
- `chore:` for build process or auxiliary tool changes

