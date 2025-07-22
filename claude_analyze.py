import os
import anthropic

def main():
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    
    # Get the comment/issue body
    comment_body = os.environ.get('COMMENT_BODY', 'Please analyze this repository')
    
    # Read repository analysis
    with open('repo_analysis.txt', 'r') as f:
        repo_info = f.read()
    
    # Analyze the repository
    response = client.messages.create(
        model='claude-3-5-haiku-20241022',
        max_tokens=1500,
        messages=[{
            'role': 'user', 
            'content': f'''You are a helpful GitHub assistant analyzing a repository.

User request: {comment_body}

Repository information:
{repo_info}

Please analyze this repository structure and provide specific insights about potential bugs, improvements, or recommendations based on the files and structure shown.'''
        }]
    )
    
    print('Claude Response:')
    print(response.content[0].text)

if __name__ == "__main__":
    main()