import jwt
from django.conf import settings
from rest_framework import authentication, exceptions, status
from oauth2_provider.oauth2_backends import get_oauthlib_core
from users.models import User


class SystemAuthentication(authentication.BaseAuthentication):

    def __init__(self):
        self.authentication_header_prefix = 'Bearer'

    @staticmethod
    def get_jwt_header(request):
        auth = request.headers.get('JWTAUTH', b'')
        return auth

    def authenticate(self, request):
        request.user = None
        oauthlib_core = get_oauthlib_core()
        valid, r = oauthlib_core.verify_request(request, scopes=[])

        if not valid:
            return None

        jwt_header = self.get_jwt_header(request).split()
        header_prefix = self.authentication_header_prefix.lower()
        if not jwt_header:
            return None
        if len(jwt_header) == 1 or len(jwt_header) > 2:
            raise exceptions.NotAuthenticated(
                {"message": "Could Not Authenticate User", "status_code": status.HTTP_401_UNAUTHORIZED}
            )

        try:
            prefix = jwt_header[0]
            token = jwt_header[1]
        except Exception:
            raise exceptions.NotAcceptable(
                {"message": "No Token Present", "status_code": status.HTTP_406_NOT_ACCEPTABLE})

        if prefix.lower() != header_prefix:
            return None
        return self.authenticate_credentials(request, token)

    @staticmethod
    def authenticate_credentials(request, token):
        try:
            decoded = jwt.decode(token, settings.TOKEN_SECRET_KEY, audience="urn:jst", algorithms=['HS512'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                {"message": "User Logged Out.Please Try Again",
                 "status_code":
                     status.HTTP_401_UNAUTHORIZED})

        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed(
                {"message": "Please Login Again",
                 "status_code":
                     status.HTTP_401_UNAUTHORIZED})

        except Exception as e:
            print(e)
            raise exceptions.AuthenticationFailed(
                {"message": "Invalid Verification",
                 "status_code": status.HTTP_401_UNAUTHORIZED})

        try:
            user = User.objects.get(id=decoded['user'])
        except User.DoesNotExist:

            raise exceptions.AuthenticationFailed(
                {"message": "Invalid User",
                 "status_code":
                     status.HTTP_401_UNAUTHORIZED})
        return user, token
