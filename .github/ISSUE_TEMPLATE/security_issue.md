---
name: Security Issue
about: Report a security vulnerability (use private reporting for sensitive issues)
title: '[SECURITY] '
labels: security, priority-high
assignees: trose

---

⚠️ **IMPORTANT**: For sensitive security vulnerabilities, please use [private security reporting](https://github.com/trose/ice-locator-mcp/security/advisories/new) instead of public issues.

## Security Issue Type
- [ ] Information disclosure
- [ ] Authentication/authorization bypass
- [ ] Injection vulnerability (XSS, SQL, etc.)
- [ ] Denial of service
- [ ] Anti-detection bypass
- [ ] Dependency vulnerability
- [ ] Configuration security issue
- [ ] Other: ___________

## Severity Assessment
- [ ] Critical (immediate threat, active exploitation possible)
- [ ] High (significant security risk)
- [ ] Medium (moderate security risk)
- [ ] Low (minor security concern)

## Affected Components
- [ ] MCP server core
- [ ] Search functionality
- [ ] Anti-detection system
- [ ] Proxy management
- [ ] Configuration handling
- [ ] Dependencies
- [ ] Documentation/examples

## Issue Description
**Clear description of the security issue (avoid sensitive details in public issues)**

## Impact
**What could an attacker achieve by exploiting this vulnerability?**

## Attack Vector
**How could this vulnerability be exploited?**
- [ ] Remote exploitation
- [ ] Local exploitation  
- [ ] Requires authentication
- [ ] No authentication required
- [ ] Requires user interaction
- [ ] No user interaction required

## Affected Versions
**Which versions are affected by this issue?**
- First affected version: 
- Last affected version:
- Fixed in version: (if known)

## Environment
- **OS**: [e.g. macOS, Linux, Windows]
- **Python Version**: [e.g. 3.10.8]
- **Package Version**: [e.g. 1.0.0]
- **Deployment**: [e.g. local, container, cloud]

## Proof of Concept
**For non-sensitive issues only. For sensitive vulnerabilities, contact privately.**

```
Steps to reproduce (if safe to share publicly)
```

## Mitigation/Workarounds
**Any temporary mitigations users can apply?**

## References
**Links to CVEs, security advisories, or documentation**

## Reporter Information
**Optional: How would you like to be credited in security advisories?**
- Name/Handle: 
- Contact: (email or other preferred method)

---

### For Maintainers

#### Immediate Response (24 hours)
- [ ] Issue acknowledged
- [ ] Severity assessment completed
- [ ] Private communication established (if needed)
- [ ] Affected versions identified

#### Investigation (72 hours)  
- [ ] Issue reproduced and confirmed
- [ ] Root cause analysis completed
- [ ] Impact assessment finalized
- [ ] Fix development started

#### Resolution (7-30 days depending on severity)
- [ ] Fix implemented and tested
- [ ] Security advisory prepared
- [ ] Coordinated disclosure planned
- [ ] Release scheduled

#### Post-Resolution
- [ ] Security advisory published
- [ ] Fix released
- [ ] Reporter credited (if desired)
- [ ] Lessons learned documented