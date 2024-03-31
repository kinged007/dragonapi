import pytest
from main import Module

class TestOpenAiModule:

    @pytest.fixture(autouse=True)
    def setup_module(self):
        self.module = Module()

    def test_completion_endpoint(self, setup_module):
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
        
        try:
            
            # Call the completion method
            response = self.module.completion(messages=messages, mock_response="This is a mockup message for debug purposes.", api_key="mockup_api_key", model="gpt-3.5-turbo")
            print(response)
            # Assert that the response is not None
            assert response is not None, "The response should not be None"

            # Check if the response has the expected attributes
            assert hasattr(response, 'choices'), "The response should have 'choices' attribute"
            assert isinstance(response.choices, list), "The 'choices' attribute should be a list"

            # Check if the response contains a message from the assistant
            assert any(choice.get('role') == 'assistant' for choice in response.choices), "The response should contain a message from the assistant"
    
        except Exception as e:
            pytest.fail(f"Error occurred: {e}")


