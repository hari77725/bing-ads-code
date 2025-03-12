from bingads.authorization import *
from bingads.service_client import ServiceClient

# Authentication credentials
DEVELOPER_TOKEN = 'BBD37VB98'  # Your developer token
CLIENT_ID = '4c0b021c-00c3-4508-838f-d3127e8167ff'  # Your client ID
ENVIRONMENT = 'sandbox'  # Use 'production' for live environment
REFRESH_TOKEN_PATH = 'refresh.txt'

def get_access_token():
    authorization_data = AuthorizationData(
        account_id=None,
        customer_id=None,
        developer_token=DEVELOPER_TOKEN,
        authentication=None
    )

    authentication = OAuthDesktopMobileAuthCodeGrant(
        client_id=CLIENT_ID,
        env=ENVIRONMENT
    )

    authorization_data.authentication = authentication

    # Try to load refresh token if it exists
    refresh_token = None
    try:
        with open(REFRESH_TOKEN_PATH, 'r') as file:
            refresh_token = file.read().strip()
    except IOError:
        pass

    if refresh_token:
        try:
            # Try to refresh the token
            tokens = authentication.request_oauth_tokens_by_refresh_token(refresh_token)
            print("Access token retrieved successfully!")
            # Save access token to file
            with open('access.txt', 'w') as file:
                file.write(tokens.access_token)
            return tokens.access_token
        except OAuthTokenRequestException:
            print("Refresh token expired or invalid. Need new authorization.")
            return None
    else:
        print("No refresh token found. Please run full OAuth flow.")
        return None

if __name__ == "__main__":
    access_token = get_access_token()
    if access_token:
        print(f"Access Token: {access_token}")