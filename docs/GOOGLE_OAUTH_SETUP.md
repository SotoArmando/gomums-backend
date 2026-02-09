# Google OAuth Setup Guide

Complete guide for integrating Google OAuth authentication in GoMums.

## 📋 Overview

GoMums supports Google OAuth for seamless sign-in/sign-up. Users can authenticate using their Google account without creating a password.

**Supported Flows:**
1. **One Tap** (Recommended) - Automatic popup for returning users
2. **Sign-In Button** - Explicit button click to authenticate

---

## 🔧 Backend Setup

### 1. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Sign-In API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen:
   - App name: "GoMums"
   - User support email: your@email.com
   - Developer contact: your@email.com
6. Create OAuth Client ID:
   - Application type: **Web application**
   - Authorized JavaScript origins:
     - `http://localhost:5173` (dev)
     - `https://yourdomain.com` (prod)
   - Authorized redirect URIs:
     - `http://localhost:5173/auth/callback` (dev)
     - `https://yourdomain.com/auth/callback` (prod)
7. Save **Client ID** and **Client Secret**

### 2. Configure Environment Variables

```bash
# .env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback
```

### 3. Implement Backend Endpoints

Update your backend to handle the OAuth endpoints defined in `API_ENDPOINTS.md`:

**POST `/auth/google`** - One Tap flow
```typescript
// Verify Google token and create/login user
import { OAuth2Client } from 'google-auth-library'

const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID)

async function verifyGoogleToken(token: string) {
  const ticket = await client.verifyIdToken({
    idToken: token,
    audience: process.env.GOOGLE_CLIENT_ID
  })
  
  const payload = ticket.getPayload()
  return {
    email: payload.email,
    name: payload.name,
    picture: payload.picture,
    googleId: payload.sub
  }
}

// In your auth controller
router.post('/auth/google', async (req, res) => {
  try {
    const { token } = req.body
    const googleUser = await verifyGoogleToken(token)
    
    // Find or create user
    let user = await db.users.findOne({ 
      where: { email: googleUser.email }
    })
    
    if (!user) {
      user = await db.users.create({
        name: googleUser.name,
        email: googleUser.email,
        oauth_provider: 'google',
        oauth_id: googleUser.googleId,
        avatar_url: googleUser.picture,
        password_hash: null // OAuth users don't have password
      })
    } else if (!user.oauth_provider) {
      // Link existing email/password account with Google
      user.oauth_provider = 'google'
      user.oauth_id = googleUser.googleId
      user.avatar_url = googleUser.picture
      await user.save()
    }
    
    // Generate JWT token
    const jwtToken = generateJWT(user)
    const refreshToken = generateRefreshToken(user)
    
    res.json({
      token: jwtToken,
      refresh_token: refreshToken,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        avatar_url: user.avatar_url,
        oauth_provider: user.oauth_provider
      }
    })
  } catch (error) {
    res.status(401).json({ error: 'Invalid Google token' })
  }
})
```

**GET `/auth/google/url`** - Redirect flow (optional)
```typescript
router.get('/auth/google/url', (req, res) => {
  const url = `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
    client_id: process.env.GOOGLE_CLIENT_ID,
    redirect_uri: process.env.GOOGLE_REDIRECT_URI,
    response_type: 'code',
    scope: 'openid email profile',
    access_type: 'offline'
  })}`
  
  res.json({ url })
})
```

**POST `/auth/google/callback`** - Handle redirect callback
```typescript
router.post('/auth/google/callback', async (req, res) => {
  const { code } = req.body
  
  // Exchange code for tokens
  const { tokens } = await client.getToken(code)
  const ticket = await client.verifyIdToken({
    idToken: tokens.id_token,
    audience: process.env.GOOGLE_CLIENT_ID
  })
  
  // Same user creation logic as above...
})
```

---

## 🎨 Frontend Setup

### 1. Add Google Sign-In Library

Add to `index.html`:
```html
<head>
  <!-- ... other tags ... -->
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
```

### 2. Configure Client ID

Update the views to use your actual Client ID:

**src/views/login-view.ts**
```typescript
// Line ~40 - Replace 'YOUR_GOOGLE_CLIENT_ID'
google.accounts.id.initialize({
  client_id: '123456789-abcdefg.apps.googleusercontent.com', // Your actual ID
  callback: (response: any) => this.handleGoogleCallback(response)
})
```

**src/views/auth-view.ts**
```typescript
// Line ~75 - Replace 'YOUR_GOOGLE_CLIENT_ID'
google.accounts.id.initialize({
  client_id: '123456789-abcdefg.apps.googleusercontent.com', // Your actual ID
  callback: (response: any) => this.handleGoogleCallback(response)
})
```

### 3. Create Auth Service

Create `src/services/api/auth.service.ts` (or update existing):

```typescript
import { httpClient } from '../../utils/http-client'

export interface AuthResponse {
  token: string
  refresh_token: string
  user: {
    id: string
    name: string
    email: string
    avatar_url?: string
    oauth_provider?: 'google' | 'facebook' | 'apple'
  }
}

class AuthService {
  async loginWithGoogle(googleToken: string): Promise<AuthResponse> {
    const response = await httpClient.post<AuthResponse>(
      '/auth/google',
      { token: googleToken }
    )
    
    // Store tokens
    localStorage.setItem('auth_token', response.token)
    localStorage.setItem('refresh_token', response.refresh_token)
    
    // Store user info
    localStorage.setItem('user', JSON.stringify(response.user))
    
    return response
  }
  
  getUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }
  
  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token')
  }
  
  logout() {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
}

export const authService = new AuthService()
```

### 4. Handle Auth in Router

Update `src/router.ts` to handle Google auth events:

```typescript
// Listen for Google auth events
document.addEventListener('google-login', async (e: CustomEvent) => {
  try {
    const { token } = e.detail
    const result = await authService.loginWithGoogle(token)
    
    console.log('User authenticated:', result.user)
    
    // Navigate to home/planning view
    router.navigate('planning')
    
    // Show success message
    showSuccessToast(`Welcome back, ${result.user.name}!`)
  } catch (error) {
    console.error('Google login failed:', error)
    showErrorToast('Failed to sign in with Google')
  }
})

document.addEventListener('google-auth', async (e: CustomEvent) => {
  // Same handler for auth-view
  try {
    const { token, mode } = e.detail
    const result = await authService.loginWithGoogle(token)
    
    const message = mode === 'signup' 
      ? `Welcome, ${result.user.name}!` 
      : `Welcome back, ${result.user.name}!`
    
    router.navigate('onboarding') // or 'planning' for signin
    showSuccessToast(message)
  } catch (error) {
    console.error('Google auth failed:', error)
    showErrorToast('Failed to authenticate with Google')
  }
})
```

---

## 🎯 User Flow

### Sign Up with Google
1. User clicks "Continue with Google" button
2. Google One Tap appears (or redirect to Google)
3. User selects Google account
4. Frontend receives Google token
5. Frontend sends token to backend `/auth/google`
6. Backend verifies token, creates user account
7. Backend returns JWT token
8. Frontend stores token, navigates to onboarding/home

### Sign In with Google
1. Same flow as sign up
2. Backend recognizes existing user by email
3. If email exists but no OAuth: links Google account
4. Returns JWT token for existing user
5. Navigates to home/planning view

---

## 🔒 Security Best Practices

1. **HTTPS**: Always use HTTPS in production
2. **Token Validation**: Verify Google tokens on backend, never trust frontend
3. **Client ID**: Store in environment variables, not hardcoded
4. **Scope Limits**: Only request necessary scopes (email, profile)
5. **Account Linking**: Allow linking Google to existing email/password accounts
6. **Token Expiry**: Implement refresh token flow for long sessions
7. **CSRF Protection**: Use state parameter in redirect flow

---

## 🧪 Testing

### Development Testing
1. Use `localhost:5173` as authorized origin
2. Test with multiple Google accounts
3. Test account linking (signup with email, then link Google)

### Production Testing
1. Add production domain to authorized origins
2. Test HTTPS enforcement
3. Verify token validation
4. Test refresh token flow

---

## 📊 Analytics & Monitoring

Track OAuth events:
```typescript
// Google Analytics
gtag('event', 'login', {
  method: 'google'
})

// Custom analytics
analytics.track('User Signed In', {
  method: 'google',
  timestamp: new Date(),
  userId: user.id
})
```

---

## 🐛 Troubleshooting

### "Popup blocked" Error
- Ensure Google library is loaded
- User must click button (no automatic prompts)
- Check popup blockers

### "Invalid token" Error
- Verify Client ID matches backend
- Check token hasn't expired
- Ensure HTTPS in production

### "Account not found" Error
- Check database connection
- Verify user creation logic
- Check email matching

### "Redirect URI mismatch"
- Update authorized redirect URIs in Google Console
- Match exact URL (including port for localhost)

---

## 📚 Resources

- [Google Sign-In Docs](https://developers.google.com/identity/gsi/web)
- [OAuth 2.0 Guide](https://oauth.net/2/)
- [Google Auth Library](https://github.com/googleapis/google-auth-library-nodejs)
- [One Tap Reference](https://developers.google.com/identity/gsi/web/guides/overview)

---

## ✅ Checklist

Backend:
- [ ] Get Google Client ID & Secret
- [ ] Add environment variables
- [ ] Implement POST `/auth/google` endpoint
- [ ] Add OAuth fields to users table
- [ ] Test token verification
- [ ] Deploy with HTTPS

Frontend:
- [ ] Add Google Sign-In script to index.html
- [ ] Update Client ID in login-view.ts
- [ ] Update Client ID in auth-view.ts
- [ ] Create/update authService
- [ ] Handle auth events in router
- [ ] Test complete flow
- [ ] Add error handling
- [ ] Add loading states

Testing:
- [ ] Test signup with Google
- [ ] Test signin with Google
- [ ] Test account linking
- [ ] Test error scenarios
- [ ] Test token refresh
- [ ] Test on mobile devices
