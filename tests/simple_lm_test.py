"""
Simple LM Studio connection test
Save as: simple_lm_test.py
"""

import openai

def test_lm_studio():
    """Test connection to LM Studio."""
    
    try:
        print("🤖 Testing LM Studio connection...")
        print(f"OpenAI library version: {openai.__version__}")
        
        # Configure OpenAI client for LM Studio
        client = openai.OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"  # LM Studio doesn't validate this
        )
        
        # Test simple completion
        response = client.chat.completions.create(
            model="local-model",  # LM Studio accepts any model name
            messages=[
                {"role": "system", "content": "You are a helpful D&D assistant."},
                {"role": "user", "content": "Say hello and confirm you're ready to help with D&D!"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        print("✅ LM Studio connected successfully!")
        print(f"Response: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nTroubleshooting:")
        print("1. Make sure LM Studio is running")
        print("2. Ensure a model is loaded")
        print("3. Check that the server is started (Local Server tab)")
        print("4. Verify the URL is http://127.0.0.1:1234")
        print("5. Try updating OpenAI library: pip install --upgrade openai")
        
        return False

if __name__ == "__main__":
    test_lm_studio()