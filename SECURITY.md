# Security Policy

## Scope

This repository contains TOML content definitions (agents, hands, MCP servers, skills, plugins, providers). Security concerns include:

- Malicious content in system prompts or descriptions
- Command injection in MCP server transport commands
- MCP server URLs pointing to phishing or malicious sites
- Credential exposure in TOML files

## Reporting a Vulnerability

**Do NOT open a public issue for security vulnerabilities.**

Email **security@librefang.dev** with:

1. Description of the vulnerability
2. Affected file(s) and content type
3. Steps to reproduce or exploit
4. Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: within 48 hours
- **Assessment**: within 5 business days
- **Fix**: dependent on severity, typically within 2 weeks

## Supported Versions

| Version | Supported |
|---------|-----------|
| main branch | Yes |
| Other branches | No |
