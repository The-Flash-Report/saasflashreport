#!/bin/bash
# PromptWire Build Script
# This script runs the aggregator to build the site locally
# It can easily be adapted for use in GitHub Actions

# Set up error handling
set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Return non-zero if any command in a pipe fails

# Log function for better output
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Create directories if they don't exist
ensure_dirs() {
  log "Ensuring directories exist..."
  mkdir -p archive
}

# Check for required environment variables
check_env() {
  log "Checking environment variables..."
  
  # Only warn if not set, don't exit (script will skip those sources)
  [[ -z "${NEWS_API_KEY}" ]] && log "WARNING: NEWS_API_KEY not set. News API results will be skipped."
  [[ -z "${PERPLEXITY_API_KEY}" ]] && log "WARNING: PERPLEXITY_API_KEY not set. Perplexity results will be skipped."
  [[ -z "${REDDIT_CLIENT_ID}" ]] && log "WARNING: REDDIT_CLIENT_ID not set. Reddit results will be skipped."
  [[ -z "${REDDIT_CLIENT_SECRET}" ]] && log "WARNING: REDDIT_CLIENT_SECRET not set. Reddit results will be skipped."
  [[ -z "${REDDIT_USER_AGENT}" ]] && log "WARNING: REDDIT_USER_AGENT not set. Default will be used."
}

# Run the aggregator
run_aggregator() {
  log "Running the aggregator..."
  python3 aggregator.py
}

# Generate sitemap
generate_sitemap() {
  log "Generating sitemap.xml..."
  python3 generate_sitemap.py
}

# Verify the output was created
verify_output() {
  log "Verifying output..."
  if [[ -f "index.html" ]]; then
    log "SUCCESS: index.html was created"
    
    # Get today's date in YYYY-MM-DD format
    TODAY=$(date '+%Y-%m-%d')
    ARCHIVE_FILE="archive/${TODAY}.html"
    
    if [[ -f "$ARCHIVE_FILE" ]]; then
      log "SUCCESS: Archive file was created: $ARCHIVE_FILE"
    else
      log "ERROR: Archive file was not created: $ARCHIVE_FILE"
      return 1
    fi

    if [[ -f "sitemap.xml" ]]; then
      log "SUCCESS: sitemap.xml was generated"
    else
      log "ERROR: sitemap.xml was not generated"
      return 1
    fi
  else
    log "ERROR: index.html was not created!"
    return 1
  fi
}

# Main execution
main() {
  log "Starting PromptWire build process..."
  
  ensure_dirs
  check_env
  run_aggregator
  generate_sitemap
  verify_output
  
  log "Build process complete!"
}

# Run main function
main 