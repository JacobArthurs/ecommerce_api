from graphene_django.utils.testing import GraphQLTestCase
from common.utils import execute_mutation
from django.contrib.auth.models import User, Group

class AuthenticationMutationTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.user.groups.add(self.user_group)

    def test_token_auth_success(self):
        mutation = """
        mutation tokenAuth($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
                token
                payload
                refreshExpiresIn
            }
        }
        """

        response = self.query(mutation, variables={'username': 'testuser', 'password': 'password'}, operation_name='tokenAuth')

        self.assertResponseNoErrors(response)
        self.assertIsNotNone(response.json()['data']['tokenAuth']['token'])
        self.assertEqual(response.json()['data']['tokenAuth']['payload']['username'], self.user.username)
        self.assertEqual(response.json()['data']['tokenAuth']['payload']['iss'], 'ecommerce.jacobarthurs.com')
        self.assertEqual(response.json()['data']['tokenAuth']['payload']['aud'], 'ecommerce.jacobarthurs.com')
        self.assertIn('user', response.json()['data']['tokenAuth']['payload']['groups'])

    def test_token_auth_fail(self):
        mutation = """
        mutation tokenAuth($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
                token
                payload
                refreshExpiresIn
            }
        }
        """

        response = self.query(mutation, variables={'username': 'wronguser', 'password': 'wrongpassword'}, operation_name='tokenAuth')

        self.assertResponseHasErrors(response)
        self.assertIn("Please enter valid credentials", str(response.content))

    def test_refresh_token_success(self):
        token_auth_mutation = """
        mutation tokenAuth($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
                token
            }
        }
        """
        response = self.query(token_auth_mutation, variables={'username': 'testuser', 'password': 'password'}, operation_name='tokenAuth')
        self.assertResponseNoErrors(response)
        token = response.json()['data']['tokenAuth']['token']

        refresh_token_mutation = """
        mutation refreshToken($token: String!) {
            refreshToken(token: $token) {
                token
                payload
                refreshExpiresIn
            }
        }
        """

        response = self.query(refresh_token_mutation, variables={'token': token}, operation_name='refreshToken')

        self.assertResponseNoErrors(response)
        self.assertIsNotNone(response.json()['data']['refreshToken']['token'])
        self.assertEqual(response.json()['data']['refreshToken']['payload']['username'], self.user.username)
        self.assertEqual(response.json()['data']['refreshToken']['payload']['iss'], 'ecommerce.jacobarthurs.com')
        self.assertEqual(response.json()['data']['refreshToken']['payload']['aud'], 'ecommerce.jacobarthurs.com')
        self.assertIn('user', response.json()['data']['refreshToken']['payload']['groups'])

    def test_refresh_token_fail(self):
        mutation = """
        mutation refreshToken($token: String!) {
            refreshToken(token: $token) {
                token
                payload
                refreshExpiresIn
            }
        }
        """

        response = self.query(mutation, variables={'token': 'badtoken.badtoken'}, operation_name='refreshToken')

        self.assertResponseHasErrors(response)
        self.assertIn("Error decoding signature", str(response.content))

    def test_verify_token_success(self):
        token_auth_mutation = """
        mutation tokenAuth($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
                token
            }
        }
        """
        response = self.query(token_auth_mutation, variables={'username': 'testuser', 'password': 'password'}, operation_name='tokenAuth')
        self.assertResponseNoErrors(response)
        token = response.json()['data']['tokenAuth']['token']

        verify_token_mutation = """
        mutation verifyToken($token: String!) {
            verifyToken(token: $token) {
                payload
            }
        }
        """

        response = self.query(verify_token_mutation, variables={'token': token}, operation_name='verifyToken')

        self.assertResponseNoErrors(response)
        self.assertEqual(response.json()['data']['verifyToken']['payload']['username'], self.user.username)
        self.assertEqual(response.json()['data']['verifyToken']['payload']['iss'], 'ecommerce.jacobarthurs.com')
        self.assertEqual(response.json()['data']['verifyToken']['payload']['aud'], 'ecommerce.jacobarthurs.com')
        self.assertIn('user', response.json()['data']['verifyToken']['payload']['groups'])

    def test_verify_token_fail(self):
        mutation = """
        mutation verifyToken($token: String!) {
            verifyToken(token: $token) {
                payload
            }
        }
        """

        response = self.query(mutation, variables={'token': 'badtoken.badtoken'}, operation_name='verifyToken')

        self.assertResponseHasErrors(response)
        self.assertIn("Error decoding signature", str(response.content))