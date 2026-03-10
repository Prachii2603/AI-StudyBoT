#!/usr/bin/env python3
"""
Setup script to configure API keys for the AI Learning Chatbot
"""

import os

def setup_api_keys():
    print("🤖 AI Learning Chatbot - API Key Setup")
    print("=" * 50)
    
    env_file_path = "backend/.env"
    
    # Read current .env file
    env_content = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_content[key] = value
    
    print("\nChoose your AI provider:")
    print("1. OpenAI (GPT-3.5/GPT-4)")
    print("2. Groq (Llama3, Mixtral, etc.)")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    if choice == '1':
        provider = 'openai'
        print("\n📝 Setting up OpenAI...")
        api_key = input("Enter your OpenAI API key: ").strip()
        env_content['AI_PROVIDER'] = 'openai'
        env_content['OPENAI_API_KEY'] = api_key
        print("✅ OpenAI configured!")
    else:
        provider = 'groq'
        print("\n📝 Setting up Groq...")
        api_key = input("Enter your Groq API key: ").strip()
        env_content['AI_PROVIDER'] = 'groq'
        env_content['GROQ_API_KEY'] = api_key
        print("✅ Groq configured!")
    
    # Write updated .env file
    with open(env_file_path, 'w') as f:
        f.write("# API Keys\n")
        for key, value in env_content.items():
            f.write(f"{key}={value}\n")
        f.write("\n# Database\n")
        f.write("DATABASE_URL=sqlite:///./learning_chatbot.db\n")
    
    print(f"\n🎉 Setup complete! Your AI provider is set to: {provider.upper()}")
    print("\n📋 Next steps:")
    print("1. Restart your backend server if it's running")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Start chatting with your AI tutor!")
    print("\n💡 You can change providers anytime by editing backend/.env")

if __name__ == "__main__":
    setup_api_keys()