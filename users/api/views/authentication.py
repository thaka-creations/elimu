@action(
        methods=['POST'],
        detail=False,
        url_name='system-login',
        url_path='system-login'
    )
    def system_login(self, request):
        payload = request.data
        payload_serializer = auth_serializers.SystemLoginSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        usertype = validated_data['user_category']
        username = validated_data['username']
        password = validated_data['password']

        if usertype not in ['PUBLIC', 'STAFF']:
            return Response({"details": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_instance = auth_models.User.objects.get(
                Q(Q(username=username) | Q(public_user__email=username) | Q(company_user__email=username)
                  | Q(staff_user__email=username))
            )
        except auth_models.User.DoesNotExist:
            return Response({"details": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        # authenticate user
        username = user_instance.username
        user = authenticate(username=username, password=password)

        if not user:
            return Response({"details": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            category_instance = services_responses. \
                get_user_category_type({"request_id": user.user_category_type, "filter_type": "id"})

            if usertype in ['PUBLIC']:
                if category_instance['name'] not in ['COMPANY', 'PUBLIC_USER']:
                    return Response({"details": "Invalid User Account"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if category_instance['name'] not in ['STAFF']:
                    return Response({"details": "Invalid User Account"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                oauth2_credentials = get_application_model().objects.get(user=user)
            except get_application_model().DoesNotExist:
                return Response({"details": "Invalid Client"}, status=status.HTTP_400_BAD_REQUEST)

        dt = {
            'grant_type': 'password',
            'username': user.username,
            'password': password,
            'client_id': oauth2_credentials.client_id,
            'client_secret': oauth2_credentials.client_secret
        }

        resp = services_responses.get_client_details(dt)

        if not resp:
            return Response({"details": "Invalid Client"}, status=status.HTTP_400_BAD_REQUEST)

        userinfo = {
            'access_token': resp['access_token'],
            'expires_in': resp['expires_in'],
            'token_type': resp['token_type'],
            'refresh_token': resp['refresh_token'],
            'jwt_token': klass.generate_jwt_token(user)
        }

        return Response({"details": userinfo}, status=status.HTTP_200_OK)