#!/usr/bin/env python3
"""
Test script to verify the daily update mechanism and debug issues.
This can be run manually to simulate what the GitHub Action does.
"""

import subprocess
import os
import datetime
import sys

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("🧪 Testing Daily Update Mechanism")
    print(f"📅 Current date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Run aggregator
    success = run_command("python3 aggregator.py", "Running aggregator script")
    if not success:
        print("❌ Aggregator failed")
        return False
    
    # Step 2: Check for changes
    run_command("git status --porcelain", "Checking git status")
    
    # Step 3: Check key files
    run_command("grep 'Updated:' index.html", "Checking current date in index.html")
    
    # Step 4: Check if files were recently modified
    run_command("find index.html processed_urls.json data/main_page_content.json -newer /tmp/test_marker 2>/dev/null || echo 'Files not found or no marker'", "Checking recently modified files")
    
    # Step 5: Show archive file
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    run_command(f"ls -la archive/{today}.html", f"Checking archive file for {today}")
    
    print("\n✅ Test completed!")
    print("\n📋 Next steps:")
    print("1. If no changes detected, check if content sources have new articles")
    print("2. If changes detected, commit and push manually to test")
    print("3. If workflow still fails, check GitHub Action logs for detailed error")

if __name__ == "__main__":
    # Create a marker file for testing modification times
    subprocess.run("touch /tmp/test_marker", shell=True)
    
    main() 