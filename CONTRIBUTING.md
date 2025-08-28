# Contributing to ICE Locator MCP Server

Thank you for your interest in contributing to the ICE Locator MCP Server! This project provides critical services for locating individuals in ICE detention, and we welcome contributions that improve its functionality, reliability, and accessibility.

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** when available
3. **Provide detailed information** including:
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Log outputs (sanitized of sensitive data)

### Submitting Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow the coding standards** (see below)
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/ice-locator-mcp.git
cd ice-locator-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 src/ tests/
black src/ tests/
```

## Coding Standards

### Python Style
- Follow **PEP 8** style guidelines
- Use **Black** for code formatting
- Use **type hints** for all functions
- Maximum line length: **88 characters**

### Code Quality
- **Write comprehensive tests** (aim for >90% coverage)
- **Use meaningful variable and function names**
- **Add docstrings** for all public functions and classes
- **Handle errors gracefully** with appropriate logging

### Security Considerations
- **Never commit sensitive data** (API keys, credentials, etc.)
- **Sanitize all user inputs**
- **Follow responsible disclosure** for security issues
- **Use anti-detection measures responsibly**

## Anti-Detection Guidelines

This project implements anti-detection measures to avoid blocking. Contributors must:

1. **Use measures responsibly** - Only to prevent automated blocking
2. **Respect rate limits** - Don't overwhelm target systems
3. **Follow legal guidelines** - Ensure compliance with applicable laws
4. **Document new techniques** - Explain anti-detection strategies clearly

## Testing

### Test Categories
- **Unit tests**: Test individual components
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Performance tests**: Test under load
- **Security tests**: Test for vulnerabilities

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Documentation

### Documentation Standards
- **Use Markdown** for all documentation
- **Keep documentation up-to-date** with code changes
- **Include examples** for complex features
- **Use clear, concise language**

### Types of Documentation
- **API documentation**: Tool specifications and schemas
- **User guides**: Installation and usage instructions
- **Developer guides**: Architecture and development setup
- **Legal documentation**: Compliance and usage guidelines

## Legal and Ethical Considerations

### Important Notice
This tool is designed to help locate individuals in ICE detention facilities for legitimate purposes such as:
- Legal representation
- Family reunification
- Humanitarian assistance

### Guidelines
- **Use responsibly** and for legitimate purposes only
- **Respect privacy** of individuals and facilities
- **Follow applicable laws** in your jurisdiction
- **Don't abuse the system** or overwhelm ICE servers
- **Maintain accuracy** of information provided

### Prohibited Uses
- Commercial exploitation of detainee information
- Harassment or stalking of individuals
- Circumventing legitimate security measures
- Any illegal or harmful activities

## Release Process

### Version Management
- Use **semantic versioning** (MAJOR.MINOR.PATCH)
- Update **CHANGELOG.md** for all releases
- Tag releases with **v** prefix (e.g., v1.0.0)

### Release Checklist
1. Update version numbers in all relevant files
2. Update CHANGELOG.md with new features and fixes
3. Run full test suite and validation scripts
4. Create GitHub release with release notes
5. Publish to PyPI (for maintainers)
6. Update MCP registry submission

## Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Pull Requests**: Code contributions and reviews

### Getting Help
- Check the **documentation** first
- Search **existing issues** for similar problems
- Ask questions in **GitHub Discussions**
- For security issues, use **private reporting**

## Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **CHANGELOG.md** for significant contributions
- **GitHub contributors** page
- **Release notes** for major contributions

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the ICE Locator MCP Server! Your contributions help provide critical services to those who need them most.