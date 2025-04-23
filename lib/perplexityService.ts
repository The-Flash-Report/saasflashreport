// lib/perplexityService.ts

interface PerplexityHeadline {
  title: string;
  url: string; // Might be a placeholder if Perplexity doesn't provide direct URLs
  source: string;
}

// IMPORTANT: Verify this model name against Perplexity API documentation
const PERPLEXITY_MODEL = 'sonar-medium-online';
const PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions";

export async function fetchPerplexityNews(): Promise<PerplexityHeadline[]> {
  const apiKey = localStorage.getItem('perplexity_api_key');

  if (!apiKey) {
    console.warn('Perplexity API key not found in localStorage.');
    // You might want to throw an error or return a specific status
    return [];
  }

  const headlines: PerplexityHeadline[] = [];
  const headers = {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/json",
    "Accept": "application/json",
  };

  // The prompt you suggested
  const query = "Give me the top 10 AI news stories, content and viral posts from the last 48 hours. Return each as a title and a working URL.";

  const payload = {
    "model": PERPLEXITY_MODEL,
    "messages": [
      {
        "role": "system",
        "content": "You are an AI news assistant. Provide a numbered list of news items based on the user query, including a title and URL for each if possible. Format clearly."
      },
      {
        "role": "user",
        "content": query
      }
    ],
     // Optional: Adjust max_tokens if needed
    // "max_tokens": 500,
  };

  try {
    console.log(`Fetching from Perplexity API with model: ${PERPLEXITY_MODEL}...`);
    const response = await fetch(PERPLEXITY_API_URL, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => response.text()); // Try to parse error, fallback to text
      console.error(`Error fetching from Perplexity API: ${response.status} ${response.statusText}`, errorBody);
      // Throwing an error might be better here depending on how you handle it in the UI
      // throw new Error(`Perplexity API Error: ${response.status} - ${JSON.stringify(errorBody)}`);
      return []; // Return empty on error for now
    }

    const data = await response.json();
    console.log("Perplexity API Response Data:", data); // Log the full response for debugging

    // --- Response Parsing Logic ---
    // IMPORTANT: This parsing is highly speculative and needs adjustment based on actual response format.
    if (data?.choices?.[0]?.message?.content) {
      const content: string = data.choices[0].message.content.trim();
      console.log("Perplexity Content:", content);

      // Attempt to split into lines and parse Title/URL
      const lines = content.split('\\n');
      lines.forEach(line => {
        // Basic attempt to find a URL in the line
        const urlMatch = line.match(/https?:\/\/[^\s]+/);
        const url = urlMatch ? urlMatch[0] : '#perplexity-fallback'; // Use fallback if no URL found

        // Assume the text before the URL (or the whole line) is the title
        let title = line.replace(url, '').trim();
        // Remove potential list numbering (e.g., "1. ", " - ")
        title = title.replace(/^[\d.\s-]+/, '').trim();

        if (title) {
          headlines.push({
            title: title,
            url: url,
            source: 'Perplexity',
          });
        }
      });
        console.log("Parsed Perplexity Headlines:", headlines);
    } else {
      console.warn("Unexpected response structure from Perplexity", data);
    }
    // --- End Parsing Logic ---


  } catch (error) {
    console.error("An unexpected error occurred fetching from Perplexity:", error);
    // Consider re-throwing or handling differently
  }

  // Limit to max 10 results as requested in the prompt, though the parsing might yield more/less
  return headlines.slice(0, 10);
} 