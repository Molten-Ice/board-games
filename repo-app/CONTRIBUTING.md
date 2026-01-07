# Contributing to Foody Menu App

Thank you for your interest in contributing to Foody Menu App! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/foody-menu-app.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- Tesseract OCR
- Git

### Local Development

1. Install Tesseract OCR (see README.md)

2. Backend setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

3. Frontend setup:
```bash
cd frontend
npm install
npm start
```

## Code Style

### Python (Backend)
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### JavaScript (Frontend)
- Use ES6+ features
- Follow React best practices
- Use functional components and hooks
- Keep components small and focused
- Use meaningful component and variable names

### CSS
- Use BEM naming convention where appropriate
- Keep styles modular and reusable
- Use CSS variables for colors and common values
- Ensure responsive design

## Commit Messages

Write clear, concise commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs when applicable

Examples:
```
Add dietary filter to menu search
Fix camera permission handling on iOS
Update OCR preprocessing for better accuracy
```

## Pull Request Process

1. **Update Documentation**: Update README.md if you change functionality
2. **Add Tests**: Add tests for new features
3. **Test Thoroughly**: Test on multiple browsers/devices if UI changes
4. **Follow Code Style**: Ensure code follows project style guidelines
5. **Describe Changes**: Provide clear description in PR
6. **Link Issues**: Reference related issues in PR description

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How you tested the changes

## Screenshots
If applicable, add screenshots

## Checklist
- [ ] Code follows project style
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] Added tests
- [ ] Tests pass locally
- [ ] No new warnings
```

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists
2. Check if there's an open issue for it
3. Create a new issue with:
   - Clear description of the feature
   - Use cases
   - Expected behavior
   - Any relevant examples or mockups

## Bug Reports

Found a bug? Please report it:

1. Check if the bug is already reported
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Environment details (OS, browser, versions)

### Bug Report Template
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Screenshots
If applicable, add screenshots

## Environment
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 96]
- Node Version: [e.g., 16.0.0]
- Python Version: [e.g., 3.9.0]
```

## Areas for Contribution

We especially welcome contributions in:

### Backend
- OCR accuracy improvements
- New dietary tag detection
- Performance optimization
- API enhancements
- Database optimizations

### Frontend
- UI/UX improvements
- Mobile responsiveness
- Accessibility features
- New filtering options
- Performance optimization

### Documentation
- Tutorial improvements
- API documentation
- Code examples
- Translation to other languages

### Testing
- Unit tests
- Integration tests
- E2E tests
- Performance tests

## Code Review Process

1. Maintainers will review PRs within a few days
2. Feedback will be provided as comments
3. Address feedback and update PR
4. Once approved, PR will be merged

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the code of conduct

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make Foody Menu App better for everyone. Thank you for being part of our community!
