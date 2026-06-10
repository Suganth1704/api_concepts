This project is to understand the REST API development

Source: https://dev-faizan.medium.com/building-production-ready-apis-with-fastapi-complete-guide-with-authentication-rate-limiting-and-391028cc623c


Install with: pip install argon2-cffi

Recommendation: Use solution #1 (pre-hash with SHA256) — it's the best balance of security and compatibility. The pre-hashing ensures consistent behavior and maintains bcrypt's security properties while handling arbitrarily long passwords.