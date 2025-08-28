# Contributing to ICE Locator MCP Server

Thank you for your interest in contributing! This guide outlines how to contribute effectively.

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ice-locator-mcp.git
cd ice-locator-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Standards

### Python Code Style
- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use Black for formatting
- Use Ruff for linting

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/ice_locator_mcp/
```

### Testing Requirements
- Write tests for all new features
- Maintain >90% code coverage
- Use pytest for testing
- Mock external dependencies

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=ice_locator_mcp --cov-report=html
```

## Contribution Types

### Bug Reports
When reporting bugs, include:
- Python version
- Package version
- Minimal reproduction code
- Expected vs actual behavior
- Error messages and stack traces

### Feature Requests
For new features:
- Describe the use case
- Explain why it's needed
- Provide implementation ideas
- Consider backward compatibility

### Code Contributions
- Follow the development workflow
- Write comprehensive tests
- Update documentation
- Follow commit message conventions

## Commit Message Format

Use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/config changes

Examples:
```
feat(search): add fuzzy matching for names
fix(proxy): handle connection timeouts properly
docs(api): update search tool examples
```

## Pull Request Process

1. **Branch Naming**: Use descriptive names
   - `feature/fuzzy-search`
   - `fix/proxy-timeout`
   - `docs/api-examples`

2. **PR Description**: Include
   - What changes were made
   - Why they were needed
   - How to test the changes
   - Related issues

3. **Review Process**:
   - All PRs require review
   - Address feedback promptly
   - Keep PRs focused and small
   - Squash commits before merging

## Areas for Contribution

### High Priority
- [ ] Improved CAPTCHA solving
- [ ] Additional fuzzy matching algorithms
- [ ] Performance optimizations
- [ ] More comprehensive tests

### Documentation
- [ ] Tutorial videos
- [ ] Use case examples
- [ ] Translation to Spanish
- [ ] API reference improvements

### Tools and Infrastructure
- [ ] Docker improvements
- [ ] CI/CD enhancements
- [ ] Release automation
- [ ] Monitoring tools

## Security

For security vulnerabilities:
- **DO NOT** open public issues
- Email: security@example.com
- Include detailed reproduction steps
- Allow time for responsible disclosure

## Legal Considerations

### Code License
- All contributions are licensed under MIT
- By contributing, you agree to this license
- Do not include copyrighted code

### Use Case Compliance
- Ensure contributions support legitimate uses
- Consider privacy and ethical implications
- Follow applicable laws and regulations

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Follow the [Code of Conduct](code-of-conduct.md)

### Communication
- Use GitHub issues for bugs/features
- Use GitHub discussions for questions
- Be patient with responses
- Provide helpful context

## Testing Guidelines

### Unit Tests
```python
# Test structure
def test_feature_name():
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result == expected_value
```

### Integration Tests
- Test complete workflows
- Use mock external services
- Test error conditions
- Verify caching behavior

### Performance Tests
- Benchmark critical paths
- Test under load
- Monitor memory usage
- Test rate limiting

## Documentation Standards

### Code Documentation
- Use docstrings for all public functions
- Include parameter types and descriptions
- Provide usage examples
- Document exceptions

```python
def search_by_name(first_name: str, last_name: str) -> SearchResult:
    """Search for detainees by name.
    
    Args:
        first_name: First name to search for
        last_name: Last name to search for
        
    Returns:
        SearchResult containing found detainees
        
    Raises:
        ValidationError: If names are invalid
        RateLimitError: If rate limit exceeded
        
    Example:
        >>> result = search_by_name("John", "Doe")
        >>> print(result.total_results)
        1
    """
```

### User Documentation
- Write for non-technical users
- Include practical examples
- Provide troubleshooting steps
- Keep up-to-date with code changes

## Release Process

### Version Numbering
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes increment MAJOR
- New features increment MINOR
- Bug fixes increment PATCH

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release
- [ ] Deploy to PyPI

## Getting Help

### For Contributors
- Check existing issues and PRs
- Read the documentation thoroughly
- Ask questions in GitHub discussions
- Join development meetings (if scheduled)

### For Maintainers
- Review PRs promptly
- Provide constructive feedback
- Help with complex technical decisions
- Maintain project roadmap

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub repository insights
- Annual contribution summaries

Thank you for contributing to ICE Locator MCP Server!