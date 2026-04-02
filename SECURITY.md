# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Mr. F seriously. If you discover a security vulnerability, please report it to us privately.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:
1. GitHub Security Advisories (preferred)
2. Email to: [INSERT SECURITY EMAIL]

### What to Include

Please include as much information as possible:
* Description of the vulnerability
* Steps to reproduce
* Potential impact
* Any suggested fixes (if applicable)

### Response Time

We aim to respond to security reports within:
* **Critical**: 24 hours
* **High**: 48 hours
* **Medium**: 1 week
* **Low**: 2 weeks

### Process

1. **Report** - You submit a vulnerability report
2. **Acknowledge** - We acknowledge receipt within the response time
3. **Investigate** - We investigate and verify the vulnerability
4. **Fix** - We develop and test a fix
5. **Release** - We release a security patch
6. **Disclose** - We publicly disclose the vulnerability (after patch is available)

### Security Best Practices for Users

When using Mr. F:

1. **API Keys**
   * Never commit API keys to git
   * Use environment variables or secret managers
   * Rotate keys regularly

2. **Code Execution**
   * Mr. F executes generated code - ensure proper sandboxing
   * Review changes before committing
   * Use in isolated environments for production

3. **Data Privacy**
   * Be cautious about what code you allow Mr. F to access
   * API calls may send code to LLM providers
   * Review provider privacy policies

4. **Access Control**
   * Limit GitHub token permissions
   * Use read-only tokens where possible
   * Review workflow permissions regularly

### Known Limitations

* Mr. F relies on external LLM providers (OpenRouter, etc.)
* Code execution happens in your environment
* Generated code should be reviewed before deployment

### Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2).

Subscribe to releases to stay informed:
https://github.com/UnTamed-Fury/mr._F/releases

---

Thank you for helping keep Mr. F secure! 🔒
