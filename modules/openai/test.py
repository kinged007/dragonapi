import unittest
from .main import Module

class TestOpenAiModule(unittest.TestCase):

    def setUp(self):
        self.module = Module()

    def test_completion_endpoint(self):
        # Mock messages to simulate a conversation
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "What's the weather like today?"
            }
        ]

        # Call the completion method
        response = self.module.completion(messages=messages)

        # Check if the response is not None
        self.assertIsNotNone(response, "The response should not be None")

        # Check if the response has the expected attributes
        self.assertTrue(hasattr(response, 'choices'), "The response should have 'choices' attribute")
        self.assertIsInstance(response.choices, list, "The 'choices' attribute should be a list")

        # Check if the response contains a message from the assistant
        self.assertTrue(any(choice.get('role') == 'assistant' for choice in response.choices), "The response should contain a message from the assistant")

if __name__ == '__main__':
    unittest.main()
