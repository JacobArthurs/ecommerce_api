from mimetypes import types_map
from django.contrib.auth.models import User, Group
from graphene_django.utils.testing import GraphQLTestCase
from common.utils import execute_mutation

class UserMutationTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', email='admin@admin.com', password='password')

        self.user.groups.add(self.user_group)
        self.admin_user.groups.add(self.admin_group)

        self.client.force_login(self.admin_user)

    def test_register_user_success(self):
        variables = {
            'username': {'type': 'String!', 'value': 'newuser'},
            'email': {'type': 'String!', 'value': 'newuser@example.com'},
            'password': {'type': 'String!', 'value': 'newpassword'}
        }

        response = execute_mutation(self, 'registerUser', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['registerUser']['operationResult']['success'])

    def test_register_user_duplicate_username(self):
        variables = {
            'username': {'type': 'String!', 'value': 'testuser'},
            'email': {'type': 'String!', 'value': 'newemail@example.com'},
            'password': {'type': 'String!', 'value': 'newpassword'}
        }

        response = execute_mutation(self, 'registerUser', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['registerUser']['operationResult']['success'])
        self.assertIn("Username already exists", response.json()['data']['registerUser']['operationResult']['message'])

    def test_register_user_invalid_email(self):
        variables = {
            'username': {'type': 'String!', 'value': 'uniqueuser'},
            'email': {'type': 'String!', 'value': 'notanemail'},
            'password': {'type': 'String!', 'value': 'newpassword'}
        }

        response = execute_mutation(self, 'registerUser', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['registerUser']['operationResult']['success'])
        self.assertIn("Enter a valid email address", response.json()['data']['registerUser']['operationResult']['message'])

    def test_make_admin_not_found(self):
        variables = {
            'userId': {'type': 'Int!', 'value': 99999}
        }

        response = execute_mutation(self, 'makeAdmin', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['makeAdmin']['operationResult']['success'])
        self.assertIn("User not found", response.json()['data']['makeAdmin']['operationResult']['message'])

    def test_make_admin_permission_denied(self):
        self.client.force_login(self.user)
        variables = {
            'userId': {'type': 'Int!', 'value': self.user.id}
        }

        response = execute_mutation(self, 'makeAdmin', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

    def test_remove_admin_not_found(self):
        variables = {
            'userId': {'type': 'Int!', 'value': 99999}
        }

        response = execute_mutation(self, 'removeAdmin', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['removeAdmin']['operationResult']['success'])
        self.assertIn("User not found", response.json()['data']['removeAdmin']['operationResult']['message'])

    def test_remove_admin_permission_denied(self):
        self.client.force_login(self.user)
        variables = {
            'userId': {'type': 'Int!', 'value': self.user.id}
        }

        response = execute_mutation(self, 'removeAdmin', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

class UserQueryTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user1 = User.objects.create_user(username='Alice', email='alice@example.com')
        self.user2 = User.objects.create_user(username='Bob', email='bob@example.com')

        self.user1.groups.add(self.user_group)
        self.user2.groups.add(self.admin_group)

    def test_all_users(self):
        query = '''
        query {
            allUsers {
                id
                username
                email
                groups
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['allUsers']), 2)

    def test_user_by_id(self):
        query = f'''
        query {{
            userById(id: {self.user1.id}) {{
                id
                username
                email
                groups
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(response.json()['data']['userById']['username'], self.user1.username)
        self.assertEqual(response.json()['data']['userById']['email'], self.user1.email)
        self.assertEqual(len(response.json()['data']['userById']['groups']), 1)
        self.assertEqual(response.json()['data']['userById']['groups'][0], 'user')

    def test_search_users_by_username(self):
        query = '''
        query {
            searchUsers(username: "Alice") {
                id
                username
                email
                groups
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchUsers']), 1)
        self.assertEqual(response.json()['data']['searchUsers'][0]['username'], 'Alice')
        self.assertEqual(response.json()['data']['searchUsers'][0]['email'], 'alice@example.com')
        self.assertEqual(len(response.json()['data']['searchUsers'][0]['groups']), 1)
        self.assertEqual(response.json()['data']['searchUsers'][0]['groups'][0], 'user')

    def test_search_users_by_email(self):
        query = '''
        query {
            searchUsers(email: "bob@example.com") {
                id
                username
                email
                groups
            }
        }
        '''

        response = self.query(query)
        
        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchUsers']), 1)
        self.assertEqual(response.json()['data']['searchUsers'][0]['username'], 'Bob')
        self.assertEqual(response.json()['data']['searchUsers'][0]['email'], 'bob@example.com')
        self.assertEqual(len(response.json()['data']['searchUsers'][0]['groups']), 1)
        self.assertEqual(response.json()['data']['searchUsers'][0]['groups'][0], 'admin')
