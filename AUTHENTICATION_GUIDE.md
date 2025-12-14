# Trame Admin Authentication System

## Overview

This is a simple yet secure local authentication system using JWT (JSON Web Tokens) with HTTP-only cookies. No database or session storage required.

## Architecture

The authentication system is split into three modular files:

1. **`backend/jwt_handler.py`** - Pure JWT token logic (create, verify)
2. **`backend/admin_login.py`** - Login route handlers and credentials
3. **`backend/routers/trame.py`** - Route registration

This separation ensures clean code organization and makes each component independently testable and reusable.

## How It Works

### 1. **JWT Tokens**
- Uses `python-jose` library for signing and verification
- Tokens contain: access_name, expiration time, and issued-at timestamp
- Signed with HS256 algorithm using a secret key

### 2. **HTTP-Only Cookies**
- Tokens stored in HTTP-only cookies (prevents XSS attacks)
- Cookie name: `trame_access_token`
- SameSite: `lax` (prevents CSRF attacks)
- Expires after 24 hours

### 3. **Password Verification**
- Passwords stored in `ACCESS_CREDENTIALS` dictionary
- Compared directly (plaintext for now - see Security Notes below)

## Routes

### `/trame/admin/{access_name}` (GET)
- Login page
- Shows password form if access_name is valid

### `/trame/admin/login` (POST)
- Handles login form submission
- Verifies password
- Creates JWT token and sets cookie
- Redirects to dashboard on success
- Shows error message on failure

### `/trame/admin/{access_name}/dashboard` (GET)
- Protected dashboard page
- Requires valid JWT token in cookie
- Redirects to login if token is missing or invalid

### `/trame/admin/{access_name}/logout` (GET)
- Clears the JWT cookie
- Redirects to login page

## Configuration

### In `backend/routers/trame.py`:

```python
# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Access credentials
ACCESS_CREDENTIALS = {
    "<username>": "password123",  # Change these!
    "sel": "password456",  # Change these!
}
```

## Security Features

✅ **Stateless** - No session storage needed
✅ **HTTP-only cookies** - JavaScript cannot access tokens (XSS protection)
✅ **Token expiration** - Automatic logout after 24 hours
✅ **SameSite cookies** - CSRF protection
✅ **Token verification** - Every request validates the JWT signature

## Security Recommendations for Production

### 🔴 CRITICAL - Before Production:

1. **Move SECRET_KEY to environment variable**
   ```python
   import os
   SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-key")
   ```

2. **Hash passwords** - Don't store plaintext!
   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   
   # Store hashed passwords
   ACCESS_CREDENTIALS = {
       "<username>": pwd_context.hash("password123"),
       "sel": pwd_context.hash("password456"),
   }
   
   # Verify with:
   pwd_context.verify(password, hashed_password)
   ```

3. **Enable HTTPS and secure cookies**
   ```python
   redirect_response.set_cookie(
       key="trame_access_token",
       value=token,
       httponly=True,
       secure=True,  # Only send over HTTPS
       samesite="strict",  # Stricter CSRF protection
   )
   ```

4. **Move credentials to environment variables or secure config**
   ```bash
   # .env file
   <username>_PASSWORD=secure_password_here
   SEL_PASSWORD=another_secure_password
   ```

5. **Add rate limiting** to prevent brute force attacks
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @router.post("/admin/login")
   @limiter.limit("5/minute")  # 5 attempts per minute
   async def login_submit(...):
       ...
   ```

6. **Add logging** for security events
   ```python
   logger.warning(f"Failed login attempt for {access_name} from {request.client.host}")
   ```

## Testing

1. Visit: `http://localhost:8000/trame/admin/<username>`
2. Enter password: `password123`
3. You should be redirected to the dashboard
4. Try accessing dashboard directly without login - should redirect to login
5. Click logout - should clear cookie and redirect to login

## Advantages of This Approach

- ✅ No database required
- ✅ No session storage needed
- ✅ Scales horizontally (stateless)
- ✅ Simple to implement and maintain
- ✅ Secure when properly configured
- ✅ Built-in expiration
- ✅ Works across multiple servers (same secret key)

## Disadvantages

- ❌ Cannot revoke tokens before expiration (unless you add a blacklist)
- ❌ Token size larger than session IDs
- ❌ Need to protect SECRET_KEY carefully

## Alternative Approaches Considered

1. **Sessions with Redis/Database** - More complex, requires infrastructure
2. **Basic Auth** - Less secure, no expiration
3. **OAuth2** - Overkill for simple admin access
4. **API Keys** - No expiration, harder to manage

## Extending the System

### Add token refresh:
```python
@router.post("/admin/refresh")
async def refresh_token(trame_access_token: str = Cookie(None)):
    access_name = verify_access_token(trame_access_token)
    if access_name:
        new_token = create_access_token(access_name, timedelta(hours=24))
        # Set new cookie...
```

### Add role-based access:
```python
def create_access_token(access_name: str, role: str, expires_delta: timedelta):
    to_encode = {
        "sub": access_name,
        "role": role,  # admin, user, etc.
        "exp": expire,
    }
```

### Add remember me:
```python
if remember_me:
    expires = timedelta(days=30)
else:
    expires = timedelta(hours=24)
```
