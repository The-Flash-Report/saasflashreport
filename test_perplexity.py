import os
import json # For pretty printing if needed
import sys

# Add the parent directory to sys.path to allow importing aggregator
# This assumes test_perplexity.py is in the same directory as aggregator.py
# If it's in a subdirectory, you might need to adjust (e.g., os.path.dirname(os.getcwd()))
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    from aggregator import fetch_perplexity_results, PERPLEXITY_API_KEY, NEWS_API_QUERY
except ImportError as e:
    print(f"Error importing from aggregator.py: {e}")
    print("Please ensure aggregator.py is in the same directory as test_perplexity.py,")
    print("or adjust the sys.path modification if it's located elsewhere.")
    sys.exit(1)

def run_perplexity_test():
    """
    Runs an isolated test of the fetch_perplexity_results function.
    """
    print("--- Starting Perplexity API Test ---")

    # Check if the API key is loaded (it would have printed a warning in aggregator.py if not)
    # We can re-check here for clarity in the test script
    actual_perplexity_key = os.environ.get("PERPLEXITY_API_KEY")
    if not actual_perplexity_key:
        print("ERROR: PERPLEXITY_API_KEY environment variable is not set.")
        print("Please set it before running the test: export PERPLEXITY_API_KEY=\"your_key\"")
        print("--- Perplexity API Test Aborted ---")
        return

    print(f"Using PERPLEXITY_API_KEY (from env var): {actual_perplexity_key[:4]}...{actual_perplexity_key[-4:] if len(actual_perplexity_key) > 8 else ''}")
    print(f"Using NEWS_API_QUERY (from aggregator.py): {NEWS_API_QUERY}\n")

    results = fetch_perplexity_results()

    print("\n--- Perplexity Results Retrieved ---")
    if results:
        print(f"Successfully retrieved {len(results)} item(s).")
        for i, item in enumerate(results):
            print(f"\nItem {i+1}:")
            print(f"  Title: {item.get('title', 'N/A')}")
            print(f"  URL: {item.get('url', 'N/A')}")
            print(f"  Source: {item.get('source', 'N/A')}")
    else:
        print("No results returned from Perplexity fetch function.")
        print("Check the logs above for any API errors or JSON decoding issues.")

    print("\n--- Perplexity API Test Finished ---")

if __name__ == "__main__":
    run_perplexity_test() 