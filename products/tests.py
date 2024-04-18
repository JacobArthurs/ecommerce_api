from django.utils import timezone
from .models import Product
from graphene_django.utils.testing import GraphQLTestCase
from common.utils import execute_mutation
from django.contrib.auth.models import User, Group

class ProductMutationTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', email='admin@admin.com', password='password')

        self.user.groups.add(self.user_group)
        self.admin_user.groups.add(self.admin_group)

        self.client.force_login(self.admin_user)
    
    def test_create_product_success(self):
        variables = {
            'name': {'type': 'String!', 'value': 'Test Name'},
            'description': {'type': 'String!', 'value': 'Test Description'},
            'cost': {'type': 'Float!', 'value': 10.75},
            'supply': {'type': 'Int!', 'value': 100}
        }

        response = execute_mutation(self, 'createProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['createProduct']['operationResult']['success'])

    def test_create_product_invalid_name(self):
        variables = {
            'name': {'type': 'String!', 'value': ''},
            'description': {'type': 'String!', 'value': 'Test Description'},
            'cost': {'type': 'Float!', 'value': 10.75},
            'supply': {'type': 'Int!', 'value': 100}
        }

        response = execute_mutation(self, 'createProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createProduct']['operationResult']['success'])
        self.assertIn("Name cannot be empty.", response.json()['data']['createProduct']['operationResult']['message'])

    def test_create_product_invalid_description(self):
        variables = {
            'name': {'type': 'String!', 'value': 'Test Name'},
            'description': {'type': 'String!', 'value': ''},
            'cost': {'type': 'Float!', 'value': 10.75},
            'supply': {'type': 'Int!', 'value': 100}
        }

        response = execute_mutation(self, 'createProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createProduct']['operationResult']['success'])
        self.assertIn("Description cannot be empty.", response.json()['data']['createProduct']['operationResult']['message'])

    def test_create_product_invalid_cost(self):
        variables = {
            'name': {'type': 'String!', 'value': 'Test Name'},
            'description': {'type': 'String!', 'value': 'Test Description'},
            'cost': {'type': 'Float!', 'value': -10.75},
            'supply': {'type': 'Int!', 'value': 100}
        }

        response = execute_mutation(self, 'createProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createProduct']['operationResult']['success'])
        self.assertIn("Cost must be a positive value.", response.json()['data']['createProduct']['operationResult']['message'])

    def test_create_product_invalid_supply(self):
        variables = {
            'name': {'type': 'String!', 'value': 'Test Name'},
            'description': {'type': 'String!', 'value': 'Test Description'},
            'cost': {'type': 'Float!', 'value': 10.75},
            'supply': {'type': 'Int!', 'value': -100}
        }

        response = execute_mutation(self, 'createProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createProduct']['operationResult']['success'])
        self.assertIn("Supply must be a positive value.", response.json()['data']['createProduct']['operationResult']['message'])

    def test_create_product_unauthorized(self):
        self.client.force_login(self.user)
        variables = {
            'name': {'type': 'String!', 'value': 'Test Name'},
            'description': {'type': 'String!', 'value': 'Test Description'},
            'cost': {'type': 'Float!', 'value': 10.75},
            'supply': {'type': 'Int!', 'value': 100}
        }

        response = execute_mutation(self, 'createProduct', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
    
    def test_update_product_success(self):
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id},
            'name': {'type': 'String!', 'value': 'Updated Name'},
            'description': {'type': 'String!', 'value': 'Updated Description'},
            'cost': {'type': 'Float!', 'value': 20.75},
            'supply': {'type': 'Int!', 'value': 200}
        }

        response = execute_mutation(self, 'updateProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['updateProduct']['operationResult']['success'])

    def test_update_product_not_found(self):
        variables = {
            'id': {'type': 'ID!', 'value': 1},
            'name': {'type': 'String!', 'value': 'Updated Name'},
            'description': {'type': 'String!', 'value': 'Updated Description'},
            'cost': {'type': 'Float!', 'value': 20.75},
            'supply': {'type': 'Int!', 'value': 200}
        }

        response = execute_mutation(self, 'updateProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateProduct']['operationResult']['success'])
        self.assertIn("Product not found.", response.json()['data']['updateProduct']['operationResult']['message'])

    def test_update_product_invalid_name(self):
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id},
            'name': {'type': 'String!', 'value': ''},
            'description': {'type': 'String!', 'value': 'Updated Description'},
            'cost': {'type': 'Float!', 'value': 20.75},
            'supply': {'type': 'Int!', 'value': 200}
        }

        response = execute_mutation(self, 'updateProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateProduct']['operationResult']['success'])
        self.assertIn("Name cannot be empty.", response.json()['data']['updateProduct']['operationResult']['message'])
    
    def test_update_product_invalid_description(self):
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id},
            'name': {'type': 'String!', 'value': 'Updated Name'},
            'description': {'type': 'String!', 'value': ''},
            'cost': {'type': 'Float!', 'value': 20.75},
            'supply': {'type': 'Int!', 'value': 200}
        }

        response = execute_mutation(self, 'updateProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateProduct']['operationResult']['success'])
        self.assertIn("Description cannot be empty.", response.json()['data']['updateProduct']['operationResult']['message'])

    def test_update_product_invalid_cost(self):
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id},
            'name': {'type': 'String!', 'value': 'Updated Name'},
            'description': {'type': 'String!', 'value': 'Updated Description'},
            'cost': {'type': 'Float!', 'value': -20.75},
            'supply': {'type': 'Int!', 'value': 200}
        }

        response = execute_mutation(self, 'updateProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateProduct']['operationResult']['success'])
        self.assertIn("Cost must be a positive value.", response.json()['data']['updateProduct']['operationResult']['message'])

    def test_update_product_invalid_supply(self):
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id},
            'name': {'type': 'String!', 'value': 'Updated Name'},
            'description': {'type': 'String!', 'value': 'Updated Description'},
            'cost': {'type': 'Float!', 'value': 20.75},
            'supply': {'type': 'Int!', 'value': -200}
        }

        response = execute_mutation(self, 'updateProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateProduct']['operationResult']['success'])
        self.assertIn("Supply must be a positive value.", response.json()['data']['updateProduct']['operationResult']['message'])

    def test_update_product_unauthorized(self):
        self.client.force_login(self.user)
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id},
            'name': {'type': 'String!', 'value': 'Updated Name'},
            'description': {'type': 'String!', 'value': 'Updated Description'},
            'cost': {'type': 'Float!', 'value': 20.75},
            'supply': {'type': 'Int!', 'value': 200}
        }

        response = execute_mutation(self, 'updateProduct', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

    def test_delete_product_success(self):
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id}
        }

        response = execute_mutation(self, 'deleteProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['deleteProduct']['operationResult']['success'])

    def test_delete_product_not_found(self):
        variables = {
            'id': {'type': 'ID!', 'value': 1}
        }

        response = execute_mutation(self, 'deleteProduct', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteProduct']['operationResult']['success'])
        self.assertIn("Product not found.", response.json()['data']['deleteProduct']['operationResult']['message'])

    def test_delete_product_unauthorized(self):
        self.client.force_login(self.user)
        product = Product.objects.create(
            name='Test Name',
            description='Test Description',
            cost=10.75,
            supply=100
        )

        variables = {
            'id': {'type': 'ID!', 'value': product.id}
        }

        response = execute_mutation(self, 'deleteProduct', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

class ProductQueryTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', email='admin@admin.com', password='password')

        self.user.groups.add(self.user_group)
        self.admin_user.groups.add(self.admin_group)

        self.client.force_login(self.admin_user)

        self.product1 = Product.objects.create(name='Journal', description='A great journal for your brain', cost=5.25, supply=10)
        self.product2 = Product.objects.create(name='Book', description='A great book for your brain', cost=10, supply=100)
    
    def test_all_products(self):
        query = '''
        query {
            allProducts {
                id
                name
                description
                cost
                supply
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['allProducts']), 2)

    def test_product_by_id(self):
        query = f'''
        query {{
            productById(id: {self.product1.id}) {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(response.json()['data']['productById']['name'], self.product1.name)
        self.assertEqual(response.json()['data']['productById']['description'], self.product1.description)
        self.assertEqual(float(response.json()['data']['productById']['cost']), self.product1.cost)
        self.assertEqual(response.json()['data']['productById']['supply'], self.product1.supply)

    def test_product_by_id_not_found(self):
        query = f'''
        query {{
            productById(id: 1) {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertIsNone(response.json()['data']['productById'])

    def test_search_products_by_name(self):
        query = f'''
        query {{
            searchProducts(name: "Book") {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchProducts']), 1)
        self.assertEqual(response.json()['data']['searchProducts'][0]['name'], self.product2.name)
        self.assertEqual(response.json()['data']['searchProducts'][0]['description'], self.product2.description)
        self.assertEqual(float(response.json()['data']['searchProducts'][0]['cost']), self.product2.cost)
        self.assertEqual(response.json()['data']['searchProducts'][0]['supply'], self.product2.supply)

    def test_search_products_by_description(self):
        query = f'''
        query {{
            searchProducts(productDescription: "journal") {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchProducts']), 1)
        self.assertEqual(response.json()['data']['searchProducts'][0]['name'], self.product1.name)
        self.assertEqual(response.json()['data']['searchProducts'][0]['description'], self.product1.description)
        self.assertEqual(float(response.json()['data']['searchProducts'][0]['cost']), self.product1.cost)
        self.assertEqual(response.json()['data']['searchProducts'][0]['supply'], self.product1.supply)
    
    def test_search_products_by_min_cost(self):
        query = f'''
        query {{
            searchProducts(minCost: 6.1) {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchProducts']), 1)
        self.assertEqual(response.json()['data']['searchProducts'][0]['name'], self.product2.name)
        self.assertEqual(response.json()['data']['searchProducts'][0]['description'], self.product2.description)
        self.assertEqual(float(response.json()['data']['searchProducts'][0]['cost']), self.product2.cost)
        self.assertEqual(response.json()['data']['searchProducts'][0]['supply'], self.product2.supply)

    def test_search_products_by_max_cost(self):
        query = f'''
        query {{
            searchProducts(maxCost: 5) {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchProducts']), 0)
    
    def test_search_products_by_min_supply(self):
        query = f'''
        query {{
            searchProducts(minSupply: 11) {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchProducts']), 1)
        self.assertEqual(response.json()['data']['searchProducts'][0]['name'], self.product2.name)
        self.assertEqual(response.json()['data']['searchProducts'][0]['description'], self.product2.description)
        self.assertEqual(float(response.json()['data']['searchProducts'][0]['cost']), self.product2.cost)
        self.assertEqual(response.json()['data']['searchProducts'][0]['supply'], self.product2.supply)

    def test_search_products_by_max_supply(self):
        query = f'''
        query {{
            searchProducts(maxSupply: 10) {{
                id
                name
                description
                cost
                supply
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchProducts']), 1)
        self.assertEqual(response.json()['data']['searchProducts'][0]['name'], self.product1.name)
        self.assertEqual(response.json()['data']['searchProducts'][0]['description'], self.product1.description)
        self.assertEqual(float(response.json()['data']['searchProducts'][0]['cost']), self.product1.cost)
        self.assertEqual(response.json()['data']['searchProducts'][0]['supply'], self.product1.supply)

    def test_products_per_month(self):
        query = f'''
        query {{
            productsPerMonth(lastNMonths: 6) {{
                month
                productCount
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['productsPerMonth']), 6)
        self.assertEqual(response.json()['data']['productsPerMonth'][5]['productCount'], 2)

    def test_products_per_month_unauthorized(self):
        self.client.force_login(self.user)
        query = f'''
        query {{
            productsPerMonth(lastNMonths: 6) {{
                month
                productCount
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))