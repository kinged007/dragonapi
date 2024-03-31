import unittest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from modules.cms.src.wordpress import Wordpress

class TestWordpressAPI(unittest.TestCase):
    def setUp(self):
        # Initialize the Wordpress class with example credentials
        self.wp = Wordpress(base_url='', username='', password='')

    def test_get_posts(self):
        posts = self.wp.get_posts()
        self.assertIsInstance(posts, list, "Expected to receive a list of posts")

    def test_create_post(self):
        new_post = {'title': 'Test Post', 'content': 'This is a test post.'}
        created_post = self.wp.create_post(new_post)
        self.assertEqual(created_post.get('title',{}).get('raw',None), new_post['title'], "Post title does not match")

    def test_get_categories(self):
        categories = self.wp.get_categories()
        self.assertIsInstance(categories, list, "Expected to receive a list of categories")

    def test_create_category(self):
        new_category = {'name': 'Test Category', 'description': 'A test category.'}
        created_category = self.wp.create_category(new_category)
        self.assertEqual(created_category.get('name'), new_category['name'], "Category name does not match")

    def test_get_tags(self):
        tags = self.wp.get_tags()
        self.assertIsInstance(tags, list, "Expected to receive a list of tags")

    def test_create_tag(self):
        new_tag = {'name': 'Test Tag'}
        created_tag = self.wp.create_tag(new_tag)
        self.assertEqual(created_tag.get('name'), new_tag['name'], "Tag name does not match")

    def test_get_media(self):
        media = self.wp.get_media()
        self.assertIsInstance(media, list, "Expected to receive a list of media items")

    def test_upload_media(self):
        # This is a placeholder for the actual file upload test
        # You would need to create a file object to test the upload_media method
        pass
    
    
    # Users endpoint requires administrator privileges
    # def test_get_users(self):
    #     users = self.wp.get_users()
    #     self.assertIsInstance(users, list, "Expected to receive a list of users")

    # def test_create_user(self):
    #     new_user = {'username': 'testuser', 'email': 'test@example.com', 'password': 'password'}
    #     created_user = self.wp.create_user(new_user)
    #     self.assertEqual(created_user.get('username'), new_user['username'], "User username does not match")

if __name__ == '__main__':
    unittest.main()
