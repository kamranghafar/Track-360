# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are currently supported:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Track360 seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly until it has been addressed

### Please Do

**Report security vulnerabilities by emailing:** [Your preferred contact email - you can add this]

Alternatively, you can use GitHub's private security advisory feature:
1. Go to the [Security tab](https://github.com/kamranghafar/Track360/security)
2. Click "Report a vulnerability"
3. Fill out the security advisory form

### What to Include

Please include the following information in your report:

- Type of vulnerability
- Full paths of affected source file(s)
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Fix Timeline**: Varies based on complexity and severity

### What Happens Next

1. We will acknowledge receipt of your vulnerability report
2. We will confirm the vulnerability and determine its impact
3. We will develop and test a fix
4. We will release a security patch
5. We will publicly disclose the vulnerability after the patch is released

## Security Best Practices for Users

### Production Deployment

When deploying Track360 in production, please follow these security guidelines:

#### 1. Environment Variables

**Always use environment variables for sensitive configuration:**

```bash
# Generate a strong SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set in your .env file
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

#### 2. Debug Mode

**Never run with DEBUG=True in production:**
```bash
DJANGO_DEBUG=False
```

#### 3. Allowed Hosts

**Configure ALLOWED_HOSTS properly:**
```bash
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

#### 4. Database Security

- Use a production-grade database (PostgreSQL, MySQL) instead of SQLite
- Use strong database passwords
- Restrict database access to localhost or specific IPs
- Regular database backups
- Encrypt database backups

#### 5. HTTPS/SSL

- Always use HTTPS in production
- Obtain SSL certificates (Let's Encrypt is free)
- Configure Django to enforce HTTPS:
  ```python
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  SECURE_HSTS_SECONDS = 31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  ```

#### 6. File Permissions

```bash
# Django code
chmod 755 /path/to/track360

# Settings file
chmod 600 dashboard_project/settings.py

# Environment file
chmod 600 .env

# Database file (if using SQLite)
chmod 600 db.sqlite3
```

#### 7. Regular Updates

- Keep Django and all dependencies up to date
- Monitor security advisories
- Apply security patches promptly
- Run: `pip list --outdated` regularly

#### 8. Access Control

- Use strong passwords for admin accounts
- Implement two-factor authentication if handling sensitive data
- Regularly review user permissions
- Remove inactive user accounts
- Use Django's built-in password validators

#### 9. Backup Strategy

- Regular automated backups
- Test backup restoration
- Store backups securely and off-site
- Encrypt backup files

#### 10. Monitoring and Logging

- Enable Django logging
- Monitor for suspicious activity
- Set up error notifications
- Review logs regularly

### Known Security Considerations

1. **SQLite in Production**: The default SQLite database is suitable for development but consider PostgreSQL or MySQL for production use with multiple users.

2. **File Upload**: If you add file upload functionality, validate file types and scan for malware.

3. **AI Assistant**: The AI assistant may have access to project data. Ensure proper access controls are in place.

4. **CSRF Tokens**: Ensure CSRF protection is enabled for all state-changing operations.

5. **XSS Protection**: User inputs are escaped by Django templates by default. Do not use `|safe` filter unless absolutely necessary.

## Security Features

Track360 includes the following security features:

- Django's built-in security middleware
- CSRF protection on all forms
- XSS protection via template auto-escaping
- Clickjacking protection (X-Frame-Options)
- SQL injection protection via ORM
- Password hashing with PBKDF2
- Secure password validation
- Session security
- User action logging

## Vulnerability Disclosure Policy

- We will acknowledge security reports within 48 hours
- We will provide an estimated timeline for fixes
- We will notify reporters when vulnerabilities are fixed
- We may ask security researchers to keep vulnerabilities confidential until patches are released
- We appreciate responsible disclosure and may recognize contributors (with permission)

## Security Hall of Fame

We recognize and thank the following individuals for responsibly disclosing security vulnerabilities:

- No vulnerabilities reported yet

## Contact

For security-related questions that are not vulnerabilities, you can:
- Open a GitHub Discussion
- Create a GitHub Issue with the "security" label (for non-sensitive topics only)

---

**Remember**: Security is a shared responsibility. Please follow best practices when deploying and using Track360.
