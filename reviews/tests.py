from django.utils import timezone
from products.models import Product
from .models import Review
from graphene_django.utils.testing import GraphQLTestCase
from common.utils import execute_mutation
from django.contrib.auth.models import User, Group


class ReviewMutationTests(GraphQLTestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name='user')
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.user.groups.add(self.user_group)
        self.client.force_login(self.user)
    
    def test_create_review_success(self):
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        variables = {
            'title': {'type': 'String!', 'value': 'Test Title'},
            'body': {'type': 'String!', 'value': 'Test Body'},
            'rating': {'type': 'Int!', 'value': 10},
            'productId': {'type': 'ID!', 'value': str(product.id)}
        }

        response = execute_mutation(self, 'createReview', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['createReview']['operationResult']['success'])

    def test_create_review_product_not_found(self):
        variables = {
            'title': {'type': 'String!', 'value': 'Test Title'},
            'body': {'type': 'String!', 'value': 'Test Body'},
            'rating': {'type': 'Int!', 'value': 10},
            'productId': {'type': 'ID!', 'value': '99999'}
        }

        response = execute_mutation(self, 'createReview', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createReview']['operationResult']['success'])
        self.assertIn("Product not found", response.json()['data']['createReview']['operationResult']['message'])

    def test_create_review_rating_invalid(self):
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        variables = {
            'title': {'type': 'String!', 'value': 'Test Title'},
            'body': {'type': 'String!', 'value': 'Test Body'},
            'rating': {'type': 'Int!', 'value': 0},
            'productId': {'type': 'ID!', 'value': str(product.id)}
        }

        response = execute_mutation(self, 'createReview', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['createReview']['operationResult']['success'])
        self.assertIn("Rating must be between 1 and 10.", response.json()['data']['createReview']['operationResult']['message'])

    def test_create_review_unauthorized(self):
        self.client.logout()
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        variables = {
            'title': {'type': 'String!', 'value': 'Test Title'},
            'body': {'type': 'String!', 'value': 'Test Body'},
            'rating': {'type': 'Int!', 'value': 10},
            'productId': {'type': 'ID!', 'value': str(product.id)}
        }

        response = execute_mutation(self, 'createReview', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
    
    def test_update_review_success(self):
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        review = Review.objects.create(title='Test Title', body='Test Body', rating=10, product=product, user=self.user)
        variables = {
            'id': {'type': 'ID!', 'value': str(review.id)},
            'title': {'type': 'String!', 'value': 'Updated Title'},
            'body': {'type': 'String!', 'value': 'Updated Body'},
            'rating': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateReview', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['updateReview']['operationResult']['success'])
    
    def test_update_review_not_found(self):
        variables = {
            'id': {'type': 'ID!', 'value': '99999'},
            'title': {'type': 'String!', 'value': 'Updated Title'},
            'body': {'type': 'String!', 'value': 'Updated Body'},
            'rating': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateReview', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateReview']['operationResult']['success'])
        self.assertIn("Review not found", response.json()['data']['updateReview']['operationResult']['message'])

    def test_update_review_rating_invalid(self):
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        review = Review.objects.create(title='Test Title', body='Test Body', rating=10, product=product, user=self.user)
        variables = {
            'id': {'type': 'ID!', 'value': str(review.id)},
            'title': {'type': 'String!', 'value': 'Updated Title'},
            'body': {'type': 'String!', 'value': 'Updated Body'},
            'rating': {'type': 'Int!', 'value': 0}
        }

        response = execute_mutation(self, 'updateReview', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateReview']['operationResult']['success'])
        self.assertIn("Rating must be between 1 and 10.", response.json()['data']['updateReview']['operationResult']['message'])

    def test_update_review_unauthorized(self):
        self.client.logout()
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        review = Review.objects.create(title='Test Title', body='Test Body', rating=10, product=product, user=self.user)
        variables = {
            'id': {'type': 'ID!', 'value': str(review.id)},
            'title': {'type': 'String!', 'value': 'Updated Title'},
            'body': {'type': 'String!', 'value': 'Updated Body'},
            'rating': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateReview', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))

    def test_update_review_user_not_author(self):
        other_user = User.objects.create_user(username='otheruser', email='other@test.com', password='password')
        self.user.groups.add(self.user_group)
        
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        review = Review.objects.create(title='Test Title', body='Test Body', rating=10, product=product, user=other_user)
        variables = {
            'id': {'type': 'ID!', 'value': str(review.id)},
            'title': {'type': 'String!', 'value': 'Updated Title'},
            'body': {'type': 'String!', 'value': 'Updated Body'},
            'rating': {'type': 'Int!', 'value': 5}
        }

        response = execute_mutation(self, 'updateReview', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['updateReview']['operationResult']['success'])
        self.assertIn("You can only update your own reviews.", response.json()['data']['updateReview']['operationResult']['message'])
    
    def test_delete_review_success(self):
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        review = Review.objects.create(title='Test Title', body='Test Body', rating=10, product=product, user=self.user)
        variables = {
            'id': {'type': 'ID!', 'value': str(review.id)}
        }

        response = execute_mutation(self, 'deleteReview', variables)

        self.assertResponseNoErrors(response)
        self.assertTrue(response.json()['data']['deleteReview']['operationResult']['success'])
    
    def test_delete_review_not_found(self):
        variables = {
            'id': {'type': 'ID!', 'value': '99999'}
        }

        response = execute_mutation(self, 'deleteReview', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteReview']['operationResult']['success'])
        self.assertIn("Review not found", response.json()['data']['deleteReview']['operationResult']['message'])
    
    def test_delete_review_unauthorized(self):
        self.client.logout()
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        review = Review.objects.create(title='Test Title', body='Test Body', rating=10, product=product, user=self.user)
        variables = {
            'id': {'type': 'ID!', 'value': str(review.id)}
        }

        response = execute_mutation(self, 'deleteReview', variables)

        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission", str(response.content))
    
    def test_delete_review_user_not_author(self):
        other_user = User.objects.create_user(username='otheruser', email='other@test.com', password='password')
        self.user.groups.add(self.user_group)
        
        product = Product.objects.create(name='Test Product', description='Test Description', cost=10, supply=10)
        review = Review.objects.create(title='Test Title', body='Test Body', rating=10, product=product, user=other_user)
        variables = {
            'id': {'type': 'ID!', 'value': str(review.id)}
        }

        response = execute_mutation(self, 'deleteReview', variables)

        self.assertResponseNoErrors(response)
        self.assertFalse(response.json()['data']['deleteReview']['operationResult']['success'])
        self.assertIn("You can only delete your own reviews.", response.json()['data']['deleteReview']['operationResult']['message'])

class ReviewQueryTests(GraphQLTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='Alice', email='alice@example.com')
        self.user2 = User.objects.create_user(username='Bob', email='bob@example.com')

        self.product1 = Product.objects.create(name='Test Product 1', description='Test Description 1', cost=10, supply=10)
        self.product2 = Product.objects.create(name='Test Product 2', description='Test Description 2', cost=10, supply=10)

        self.review1 = Review.objects.create(
            title='Great Product',
            body='This product is great!',
            rating=8,
            product=self.product1,
            user=self.user1,
        )

        self.review1.created_at = timezone.make_aware(timezone.datetime(2022, 1, 1, 0, 0, 0))
        self.review1.save()

        self.review2 = Review.objects.create(
            title='Bad Product',
            body='This product is bad!',
            rating=1,
            product=self.product1,
            user=self.user2,
        )

        self.review2.created_at = timezone.make_aware(timezone.datetime(2023, 1, 1, 0, 0, 0))
        self.review2.save()
        
        self.review3 = Review.objects.create(
            title='Ok Product',
            body='This product is ok!',
            rating=9,
            product=self.product2,
            user=self.user1,
        )

        self.review3.created_at = timezone.make_aware(timezone.datetime(2024, 1, 1, 0, 0, 0))
        self.review3.save()

    def test_all_reviews(self):
        query = '''
        query {
            allReviews {
                id
                title
                body
                rating
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['allReviews']), 3)

    def test_review_by_id(self):
        query = f'''
        query {{
            reviewById(id: {self.review1.id}) {{
                id
                title
                body
                rating
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(response.json()['data']['reviewById']['title'], self.review1.title)
        self.assertEqual(response.json()['data']['reviewById']['body'], self.review1.body)
        self.assertEqual(response.json()['data']['reviewById']['rating'], self.review1.rating)

    def test_review_by_id_not_found(self):
        query = '''
        query {
            reviewById(id: 99999) {
                id
                title
                body
                rating
            }
        }
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertIsNone(response.json()['data']['reviewById'])
    
    def test_search_reviews_by_title(self):
        query = f'''
        query {{
            searchReviews(productId: {self.product1.id}, title: "Great") {{
                id
                title
                body
                rating
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchReviews']), 1)

    def test_search_reviews_by_body(self):
        query = f'''
        query {{
            searchReviews(productId: {self.product1.id}, body: "bad") {{
                id
                title
                body
                rating
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchReviews']), 1)
    
    def test_search_reviews_by_min_rating(self):
        query = f'''
        query {{
            searchReviews(productId: {self.product2.id}, minRating: 9) {{
                id
                title
                body
                rating
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchReviews']), 1)
    
    def test_search_reviews_by_max_rating(self):
        query = f'''
        query {{
            searchReviews(productId: {self.product1.id}, maxRating: 1) {{
                id
                title
                body
                rating
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchReviews']), 1)
    
    def test_search_reviews_by_start_date(self):
        query = f'''
        query {{
            searchReviews(productId: {self.product1.id}, startDate: "2023-01-01") {{
                id
                title
                body
                rating
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchReviews']), 1)
    
    def test_search_reviews_by_end_date(self):
        query = f'''
        query {{
            searchReviews(productId: {self.product1.id}, endDate: "2023-01-01") {{
                id
                title
                body
                rating
                createdAt
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchReviews']), 2)
    
    def test_search_reviews_product_not_found(self):
        query = f'''
        query {{
            searchReviews(productId: 99999) {{
                id
                title
                body
                rating
            }}
        }}
        '''

        response = self.query(query)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response.json()['data']['searchReviews']), 0)