from products.models import Product
from .models import Tag
from graphene_django.utils.testing import GraphQLTestCase
from common.utils import execute_mutation
from django.contrib.auth.models import User, Group

class TagMutationTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', email='admin@admin.com', password='password')

        self.user.groups.add(self.user_group)
        self.admin_user.groups.add(self.admin_group)

        self.client.force_login(self.admin_user)

    def test_create_tag_success(self):
        variables = {
            'name': {'type': 'String!', 'value': 'Eco-friendly'},
            'description': {'type': 'String!', 'value': 'Products that are environmentally friendly'}
        }

        response = execute_mutation(self, 'createTag', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['createTag']['operationResult']['success'])

    def test_create_tag_permission_denied(self):
        self.client.force_login(self.user)
        variables = {
            'name': {'type': 'String!', 'value': 'Unauthorized Tag'},
            'description': {'type': 'String!', 'value': 'Unauthorized description'}
        }

        response = execute_mutation(self, 'createTag', variables)
        
        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

    def test_update_tag_success(self):
        tag = Tag.objects.create(name="Old Tag", description="Old description")
        variables = {
            'id': {'type': 'ID!', 'value': str(tag.id)},
            'name': {'type': 'String!', 'value': 'Updated Tag'},
            'description': {'type': 'String!', 'value': 'Updated description'}
        }

        response = execute_mutation(self, 'updateTag', variables)
        
        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['updateTag']['operationResult']['success'])

    def test_update_tag_invalid_id(self):
        variables = {
            'id': {'type': 'ID!', 'value': '999999'},
            'name': {'type': 'String!', 'value': 'Updated Tag'},
            'description': {'type': 'String!', 'value': 'Updated description'}
        }

        response = execute_mutation(self, 'updateTag', variables)
        
        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateTag']['operationResult']['success'])
        self.assertIn('Tag not found.', response.json()['data']['updateTag']['operationResult']['message'])

    def test_update_tag_permission_denied(self):
        self.client.force_login(self.user)
        tag = Tag.objects.create(name="Old Tag", description="Old description")
        variables = {
            'id': {'type': 'ID!', 'value': str(tag.id)},
            'name': {'type': 'String!', 'value': 'Updated Tag'},
            'description': {'type': 'String!', 'value': 'Updated description'}
        }

        response = execute_mutation(self, 'updateTag', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

    def test_delete_tag_success(self):
        tag = Tag.objects.create(name="To be deleted", description="Delete me")
        variables = {
            'id': {'type': 'ID!', 'value': str(tag.id)}
        }

        response = execute_mutation(self, 'deleteTag', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['deleteTag']['operationResult']['success'])

    def test_delete_tag_invalid_id(self):
        variables = {
            'id': {'type': 'ID!', 'value': '999999'}
        }

        response = execute_mutation(self, 'deleteTag', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteTag']['operationResult']['success'])
        self.assertIn('Tag not found.', response.json()['data']['deleteTag']['operationResult']['message'])

    def test_delete_tag_permission_denied(self):
        self.client.force_login(self.user)
        tag = Tag.objects.create(name="To be deleted", description="Delete me")
        variables = {
            'id': {'type': 'ID!', 'value': str(tag.id)}
        }

        response = execute_mutation(self, 'deleteTag', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

    def test_add_tag_to_product_success(self):
        product = Product.objects.create(name="Sample Product", description="Sample description", cost=10.10, supply=10)
        tag = Tag.objects.create(name="Sample Tag", description="Sample description")
        variables = {
            'productId': {'type': 'ID!', 'value': str(product.id)},
            'tagId': {'type': 'ID!', 'value': str(tag.id)}
        }

        response = execute_mutation(self, 'addTagToProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['addTagToProduct']['operationResult']['success'])

    def test_add_tag_to_product_invalid_tag_id(self):
        product = Product.objects.create(name="Sample Product", description="Sample description", cost=10.10, supply=10)
        variables = {
            'productId': {'type': 'ID!', 'value': str(product.id)},
            'tagId': {'type': 'ID!', 'value': '999999'}
        }

        response = execute_mutation(self, 'addTagToProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['addTagToProduct']['operationResult']['success'])
        self.assertIn('Tag not found.', response.json()['data']['addTagToProduct']['operationResult']['message'])

    def test_add_tag_to_product_invalid_product_id(self):
        tag = Tag.objects.create(name="Sample Tag", description="Sample description")
        variables = {
            'productId': {'type': 'ID!', 'value': '999999'},
            'tagId': {'type': 'ID!', 'value': str(tag.id)}
        }

        response = execute_mutation(self, 'addTagToProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['addTagToProduct']['operationResult']['success'])
        self.assertIn('Product not found.', response.json()['data']['addTagToProduct']['operationResult']['message'])

    def test_add_tag_to_product_permission_denied(self):
        self.client.force_login(self.user)
        product = Product.objects.create(name="Sample Product", description="Sample description", cost=10.10, supply=10)
        tag = Tag.objects.create(name="Sample Tag", description="Sample description")
        variables = {
            'productId': {'type': 'ID!', 'value': str(product.id)},
            'tagId': {'type': 'ID!', 'value': str(tag.id)}
        }

        response = execute_mutation(self, 'addTagToProduct', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

class TagQueryTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', email='admin@admin.com', password='password')

        self.user.groups.add(self.user_group)
        self.admin_user.groups.add(self.admin_group)

        self.client.force_login(self.admin_user)

        self.tag1 = Tag.objects.create(name="Nature", description="All about nature")
        self.tag2 = Tag.objects.create(name="Tech", description="Latest tech trends")

    def test_all_tags(self):
        query = '''
        query {
            allTags {
                id
                name
                description
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['allTags']), 2)

    def test_all_tags_permission_denied(self):
        self.client.force_login(self.user)
        query = '''
        query {
            allTags {
                id
                name
                description
            }
        }
        '''

        response = self.query(query)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
        self.assertIsNone(response.json()['data']['allTags'])

    def test_tag_by_id(self):
        query = f'''
        query {{
            tagById(id: {self.tag1.id}) {{
                id
                name
                description
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(response.json()['data']['tagById']['name'], self.tag1.name)
        self.assertEqual(response.json()['data']['tagById']['description'], self.tag1.description)

    def test_tag_by_id_does_not_found(self):
        query = f'''
        query {{
            tagById(id: 999999) {{
                id
                name
                description
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertIsNone(response.json()['data']['tagById'])

    def test_tag_by_id_permission_denied(self):
        self.client.force_login(self.user)
        query = f'''
        query {{
            tagById(id: {self.tag1.id}) {{
                id
                name
                description
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
        self.assertIsNone(response.json()['data']['tagById'])

    def test_search_tags_by_name(self):
        query = f'''
        query {{
            searchTags(name: "{self.tag1.name}") {{
                id
                name
                description
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchTags']), 1)
        self.assertEqual(response.json()['data']['searchTags'][0]['name'], self.tag1.name)
        self.assertEqual(response.json()['data']['searchTags'][0]['description'], self.tag1.description)

    def test_search_tags_by_description(self):
        query = f'''
        query {{
            searchTags(tagDescription: "{self.tag2.description}") {{
                id
                name
                description
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchTags']), 1)
        self.assertEqual(response.json()['data']['searchTags'][0]['name'], self.tag2.name)
        self.assertEqual(response.json()['data']['searchTags'][0]['description'], self.tag2.description)
    
    def test_search_tags_permission_denied(self):
        self.client.force_login(self.user)
        query = '''
        query {
            searchTags{
                id
                name
                description
            }
        }
        '''

        response = self.query(query)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
        self.assertIsNone(response.json()['data']['searchTags'])