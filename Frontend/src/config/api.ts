/**
 * API Configuration Utility
 * Detects the correct API URL based on environment
 */

export function getAPIBaseURL(): string {
  // If VITE_API_URL is explicitly set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // If we're in GitHub Codespaces
  const hostname = window.location.hostname;
  if (hostname.includes('.app.github.dev')) {
    // Extract codespace name from hostname (e.g., user-repo-hash-5173.app.github.dev)
    const match = hostname.match(/^([^-]+-.+?)-\d+\.app\.github\.dev$/);
    if (match) {
      const codespaceName = match[1];
      return `https://${codespaceName}-8001.app.github.dev`;
    }
  }
  
  // Default to localhost:8001
  return 'http://localhost:8001';
}

// Export the URL for use in other files
export const API_BASE_URL = getAPIBaseURL();
