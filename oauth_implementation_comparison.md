# Understanding OAuth 2.0 Authorization Code Flow: Web Apps vs Serverless Functions

Both implementations use the Authorization Code flow, but they represent different stages of the OAuth lifecycle.

## OAuth 2.0 Authorization Code Flow: The Complete Picture

The Authorization Code flow consists of several distinct phases:

1. **Initial Authorization**
   - Redirect user to authorization server
   - User authenticates and grants consent
   - Authorization server returns an authorization code

2. **Token Exchange**
   - Application exchanges authorization code for access/refresh tokens
   - Access token is short-lived (typically 1 hour)
   - Refresh token is long-lived (can be days, weeks, or months)

3. **Token Maintenance**
   - Application uses refresh token to obtain new access tokens
   - No user interaction required during this phase
   - Continues until refresh token expires or is revoked

4. **API Access**
   - Application uses valid access token to make API requests
   - Token must be included in authorization header

## Django Web Application Implementation (Full Flow)

Django implementation (`oauth_bingads.py`) handles the **complete** Authorization Code flow:

### 1. User Authentication Initiation

```python
@csrf_exempt
def bingads_oauth(request, ac_seq):
    """Handles OAuth authorization initiation."""
    # ... code omitted for brevity
    
    # Create authentication object
    authentication = create_web_authentication()
    authentication.state = encoded_state
    
    # Get authorization URL
    auth_url = authentication.get_authorization_endpoint()
    
    return redirect(auth_url)
```

This function:
- Creates a state parameter for security
- Generates the authorization URL
- Redirects the user to Microsoft's login page

### 2. Callback Handler and Token Exchange

```python
@csrf_exempt
def bingads_cb_redirect(request):
    """Handle the final OAuth callback redirect and token exchange."""
    # ... code omitted for brevity
    
    # Get the authorization code from the callback
    auth_code = request.GET.get('code')
    
    # Build token request
    token_request_data = {
        "client_id": BINGADS_CLIENT_ID,
        "client_secret": BINGADS_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": callback_url,
        "scope": "https://ads.microsoft.com/msads.manage offline_access"
    }
    
    # Exchange the code for tokens
    req = urllib.request.Request(TOKEN_ENDPOINT, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        token_response = json.loads(response.read().decode('utf-8'))
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
```

This function:
- Receives the authorization code via the redirect URI
- Exchanges code for access and refresh tokens
- Stores the tokens in the database

### 3. Token Storage

```python
# Save Tokens
if access_token:
    if config:
        config_data = config.data or {}
        config_data['oauthToken'] = {
            'token': access_token,
            'refresh_token': refresh_token,
            'account_id': (get_accounts_response.AccountInfo[0].Id
                          if (get_accounts_response is not None and
                              hasattr(get_accounts_response, 'AccountInfo') and
                              get_accounts_response.AccountInfo and
                              len(get_accounts_response.AccountInfo) > 0)
                          else None)
        }
        config.data = config_data
        config.save()
```

The Django app:
- Persists tokens in the database
- Associates them with user account information
- Makes them available for future API requests

### 4. User Experience

The Django implementation provides a complete user experience:
- Displays login prompts
- Shows consent screens
- Renders success/failure pages
- Allows account selection after authentication

## Google Cloud Function Implementation (Refresh Token Leg Only)

 Google Cloud Function implementation handles **only the token maintenance** portion of the flow:

```python
def get_authorization_data(oauth_config: Dict[str, Any]) -> AuthorizationData:
    """Creates BingAds authorization data using OAuth config"""
    account_id = oauth_config.get("oauthToken", {}).get('account_id')
    customer_id = oauth_config.get("oauthToken", {}).get('customer_id')
    
    if not account_id or not customer_id:
        raise ValueError("account_id and customer_id are required in oauth_config")
    
    auth = AuthorizationData(
        account_id=account_id,
        customer_id=customer_id,
        developer_token=BING_ADS_DEVELOPER_TOKEN,
        authentication = OAuthWebAuthCodeGrant(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        env=BING_ADS_ENVIRONMENT,
        redirection_uri='https://login.microsoftonline.com/common/oauth2/nativeclient',
        )
    )
    
    refresh_token = oauth_config.get('oauthToken', {}).get('refresh_token')
    if refresh_token:
        auth.authentication.request_oauth_tokens_by_refresh_token(refresh_token)
    else:
        # Critical auth warning - keep this print
        print("Warning: No refresh token found. Using default authentication.")
    return auth
```

This function:
- Retrieves a previously stored refresh token from the database
- Creates an authentication object with necessary credentials
- Uses `request_oauth_tokens_by_refresh_token()` to get a fresh access token
- No user interaction or browser redirection is involved



## Technical Implementation Details

### Django Web App OAuth Flow Details

1. **Authentication Initialization**
   - User visits a page in the Django app
   - App constructs the Microsoft OAuth authorization URL
   - App redirects user's browser to Microsoft

2. **User Authentication**
   - User logs in to Microsoft account
   - Microsoft displays consent screen showing requested permissions
   - User grants consent to the application

3. **Authorization Code Receipt**
   - Microsoft redirects back to the app's callback URL
   - Authorization code is included as a query parameter
   - Django app extracts the code

4. **Token Exchange**
   - App sends POST request to token endpoint
   - Request includes authorization code and client credentials
   - Microsoft validates request and returns tokens

5. **Session and Storage**
   - Access token used for immediate API calls
   - Refresh token stored in the database
   - User shown success page with account selection options

### Google Cloud Function OAuth Flow Details

1. **Function Invocation**
   - Cloud Function triggered by HTTP request or event
   - Function initializes BingAds client library

2. **Token Retrieval**
   - Function fetches stored configuration from database
   - Configuration includes previously obtained refresh token
   - No user interaction occurs

3. **Token Refresh**
   - Function calls `request_oauth_tokens_by_refresh_token()`
   - SDK handles token exchange with Microsoft
   - New access token provided by Microsoft

4. **API Access**
   - Function uses fresh access token for API calls
   - All communication happens server-to-server
   - Results processed as needed by the function


