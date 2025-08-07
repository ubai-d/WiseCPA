# OpenAI API Setup

## Step 1: Create .env file

Create a file named `.env` in the root directory (D:\WiseCPA\.env) with:

```
OPENAI_API_KEY=your-actual-api-key-here
```

## Step 2: Get your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key and paste it in your .env file

## Step 3: Test the setup

The app will now use OpenAI GPT-4 instead of local Mistral, which should be much faster and won't lag your system!

## Example .env file:

```
OPENAI_API_KEY=sk-proj-abc123def456ghi789...
```

