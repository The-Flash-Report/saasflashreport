import os
import anthropic
import requests

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
    
    claude_response = response.content[0].text
    print('Claude Response:')
    print(claude_response)
    
    # Post response back to GitHub issue/PR
    github_token = os.environ.get('GITHUB_TOKEN')
    issue_url = os.environ.get('ISSUE_URL')
    
    print(f'Debug: GitHub Token present: {bool(github_token)}')
    print(f'Debug: Issue URL: {issue_url}')
    
    if github_token and issue_url:
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        comment_data = {
            'body': f'🤖 **Claude Analysis:**\n\n{claude_response}'
        }
        
        try:
            response = requests.post(issue_url, json=comment_data, headers=headers)
            print(f'Response status: {response.status_code}')
            if response.status_code == 201:
                print('Successfully posted comment to GitHub issue!')
            else:
                print(f'Failed to post comment: {response.status_code} - {response.text}')
        except Exception as e:
            print(f'Error posting comment: {e}')
    else:
        print('Missing GitHub token or issue URL - cannot post comment')

if __name__ == "__main__":
    main()