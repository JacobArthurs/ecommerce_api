from django.utils import timezone

from .types import CreateOrderInput
from products.models import Product
from .models import Order, OrderItem
from graphene_django.utils.testing import GraphQLTestCase
from common.utils import execute_mutation
from django.contrib.auth.models import User, Group

class OrderMutationTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user1 = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.user2 = User.objects.create_user(username='testuser2', email='test2@test.com', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', email='admin@admin.com', password='password')

        self.user1.groups.add(self.user_group)
        self.user2.groups.add(self.user_group)
        self.admin_user.groups.add(self.admin_group)

        self.client.force_login(self.user1)

    def test_create_order_sucess(self):
        product1 = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        product2 = Product.objects.create(name='Product 2', description='Product 2 Description', cost=5, supply=20)

        order_items = [
            {"productId": product1.id, "quantity": 1},
            {"productId": product2.id, "quantity": 2}
        ]

        variables = {
            'orderItems': {'type': '[CreateOrderInput]!', 'value': order_items}
        }

        response = execute_mutation(self, 'createOrder', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['createOrder']['operationResult']['success'])

    def test_create_order_invalid_quantity(self):
        product1 = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)

        order_items = [
            {"productId": product1.id, "quantity": 0}
        ]

        variables = {
            'orderItems': {'type': '[CreateOrderInput]!', 'value': order_items}
        }

        response = execute_mutation(self, 'createOrder', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createOrder']['operationResult']['success'])
        self.assertIn("One or more quantities are less than 1.", response.json()['data']['createOrder']['operationResult']['message'])

    def test_create_order_invalid_product(self):
        order_items = [
            {"productId": 9999, "quantity": 1}
        ]

        variables = {
            'orderItems': {'type': '[CreateOrderInput]!', 'value': order_items}
        }

        response = execute_mutation(self, 'createOrder', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createOrder']['operationResult']['success'])
        self.assertIn("One or more products not found.", response.json()['data']['createOrder']['operationResult']['message'])

    def test_create_order_unauthorized(self):
        self.client.logout()

        product1 = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)

        order_items = [
            {"productId": product1.id, "quantity": 1}
        ]

        variables = {
            'orderItems': {'type': '[CreateOrderInput]!', 'value': order_items}
        }

        response = execute_mutation(self, 'createOrder', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
    
    def test_update_order_item_success(self):
        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id},
            'quantity': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['updateOrderItem']['operationResult']['success'])

    def test_update_order_item_admin_success(self):
        self.client.force_login(self.admin_user)
        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id},
            'quantity': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['updateOrderItem']['operationResult']['success'])

    def test_update_order_item_not_found(self):
        variables = {
            'id': {'type': 'ID!', 'value': 9999},
            'quantity': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateOrderItem']['operationResult']['success'])
        self.assertIn("Order item not found", response.json()['data']['updateOrderItem']['operationResult']['message'])

    def test_update_order_item_invalid_quantity(self):
        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id},
            'quantity': {'type': 'Int!', 'value': 0}
        }

        response = execute_mutation(self, 'updateOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateOrderItem']['operationResult']['success'])
        self.assertIn("One or more quantities are less than 1.", response.json()['data']['updateOrderItem']['operationResult']['message'])

    def test_update_order_item_invalid_user(self):
        self.client.force_login(self.user2)
        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id},
            'quantity': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateOrderItem']['operationResult']['success'])
        self.assertIn("You can only edit your own orders.", response.json()['data']['updateOrderItem']['operationResult']['message'])

    def test_update_order_item_unauthorized(self):
        self.client.logout()

        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id},
            'quantity': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateOrderItem', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

    def test_delete_order_success(self):
        order = Order.objects.create(user=self.user1)

        variables = {
            'id': {'type': 'ID!', 'value': order.id}
        }

        response = execute_mutation(self, 'deleteOrder', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['deleteOrder']['operationResult']['success'])

    def test_delete_order_not_found(self):
        variables = {
            'id': {'type': 'ID!', 'value': 9999}
        }

        response = execute_mutation(self, 'deleteOrder', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteOrder']['operationResult']['success'])
        self.assertIn("Order not found", response.json()['data']['deleteOrder']['operationResult']['message'])

    def test_delete_order_invalid_user(self):
        self.client.force_login(self.user2)
        order = Order.objects.create(user=self.user1)

        variables = {
            'id': {'type': 'ID!', 'value': order.id}
        }

        response = execute_mutation(self, 'deleteOrder', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteOrder']['operationResult']['success'])
        self.assertIn("You can only delete your own orders.", response.json()['data']['deleteOrder']['operationResult']['message'])

    def test_delete_order_unauthorized(self):
        self.client.logout()

        order = Order.objects.create(user=self.user1)

        variables = {
            'id': {'type': 'ID!', 'value': order.id}
        }

        response = execute_mutation(self, 'deleteOrder', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
    
    def test_delete_order_item_success(self):
        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id}
        }

        response = execute_mutation(self, 'deleteOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['deleteOrderItem']['operationResult']['success'])

    def test_delete_order_item_not_found(self):
        variables = {
            'id': {'type': 'ID!', 'value': 9999}
        }

        response = execute_mutation(self, 'deleteOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteOrderItem']['operationResult']['success'])
        self.assertIn("Order item not found", response.json()['data']['deleteOrderItem']['operationResult']['message'])
    
    def test_delete_order_item_invalid_user(self):
        self.client.force_login(self.user2)
        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id}
        }

        response = execute_mutation(self, 'deleteOrderItem', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteOrderItem']['operationResult']['success'])
        self.assertIn("You can only delete your own orders.", response.json()['data']['deleteOrderItem']['operationResult']['message'])

    def test_delete_order_item_unauthorized(self):
        self.client.logout()

        order = Order.objects.create(user=self.user1)
        product = Product.objects.create(name='Product 1', description='Product 1 Description', cost=10.75, supply=100)
        order_item = OrderItem.objects.create(
            product = product,
            cost = 11,
            quantity = 1,
            order = order
        )

        variables = {
            'id': {'type': 'ID!', 'value': order_item.id}
        }

        response = execute_mutation(self, 'deleteOrderItem', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

class OrderQueryTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')

        self.user1 = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.user2 = User.objects.create_user(username='testuser2', email='test2@test.com', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', email='admin@admin.com', password='password')

        self.user1.groups.add(self.user_group)
        self.user2.groups.add(self.user_group)
        self.admin_user.groups.add(self.admin_group)

        self.client.force_login(self.user1)

        product1 = Product.objects.create(name='Journal', description='A great journal for your brain', cost=5.25, supply=10)
        product2 = Product.objects.create(name='Book', description='A great book for your brain', cost=10, supply=100)

        self.order1 = Order.objects.create(user=self.user1, total_cost=55.25)
        self.order1Item1 = OrderItem.objects.create(product=product1, cost=5.25, quantity=1, order=self.order1)
        self.order1Item2 = OrderItem.objects.create(product=product2, cost=10, quantity=5, order=self.order1)

        self.order2 = Order.objects.create(user=self.user1, total_cost=45.25)
        self.order2.created_at = timezone.make_aware(timezone.datetime(2022, 1, 1, 0, 0, 0))
        self.order2.save()

        self.order2Item1 = OrderItem.objects.create(product=product1, cost=5.25, quantity=1, order=self.order2)
        self.order2Item2 = OrderItem.objects.create(product=product2, cost=10, quantity=4, order=self.order2)

    def test_all_orders(self):
        query = '''
        query {
            allOrders {
                id
                totalCost
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['allOrders']), 2)

    def test_all_orders_invalid_user(self):
        self.client.force_login(self.user2)

        query = '''
        query {
            allOrders {
                id
                totalCost
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['allOrders']), 0)
    
    def test_all_orders_unauthorized(self):
        self.client.logout()

        query = '''
        query {
            allOrders {
                id
                totalCost
            }
        }
        '''

        response = self.query(query)

        self.assertResponseHasErrors(response)

    def test_order_by_id(self):
        query = f'''
        query {{
            orderById(id: {self.order1.id}) {{
                id
                totalCost
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(float(response.json()['data']['orderById']['totalCost']), 55.25)

    def test_order_by_id_invalid_user(self):
        self.client.force_login(self.user2)

        query = f'''
        query {{
            orderById(id: {self.order1.id}) {{
                id
                totalCost
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(response.json()['data']['orderById'], None)

    def test_search_orders_by_min_cost(self):
        query = f'''
        query {{
            searchOrders(minCost: 50) {{
                id
                totalCost
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchOrders']), 1)

    def test_search_orders_by_max_cost(self):
        query = f'''
        query {{
            searchOrders(maxCost: 50) {{
                id
                totalCost
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchOrders']), 1)

    def test_search_orders_by_start_date(self):
        query = f'''
        query {{
            searchOrders(startDate: "2022-01-01") {{
                id
                totalCost
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchOrders']), 2)

    def test_search_orders_by_end_date(self):
        query = f'''
        query {{
            searchOrders(endDate: "2022-01-01") {{
                id
                totalCost
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchOrders']), 1)

    def test_orders_per_month(self):
        self.client.force_login(self.admin_user)
        query = '''
        query {
            ordersPerMonth(lastNMonths: 6) {
                orderCount
                orderCost
                month
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['ordersPerMonth']), 6)
        self.assertEqual(response.json()['data']['ordersPerMonth'][5]['orderCount'], 1)
        self.assertEqual(float(response.json()['data']['ordersPerMonth'][5]['orderCost']), 55.25)

    def test_orders_per_month_unauthorized(self):
        self.client.logout()

        query = '''
        query {
            ordersPerMonth(lastNMonths: 6) {
                orderCount
                orderCost
                month
            }
        }
        '''

        response = self.query(query)

        self.assertResponseHasErrors(response)