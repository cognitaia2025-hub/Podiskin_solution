/**
 * Secure Session Service
 * Manages secure voice sessions with backend
 * NEVER exposes API keys to client
 */

import { SessionConfig, SessionToken } from '../types';

export class SecureSessionService {
  private backendUrl: string;
  private currentToken: SessionToken | null = null;
  private tokenRefreshTimer: NodeJS.Timeout | null = null;

  constructor(backendUrl: string) {
    this.backendUrl = backendUrl;
  }

  /**
   * Start a new secure voice session
   * Backend creates session and returns ephemeral token
   */
  async startSession(config: SessionConfig): Promise<SessionToken> {
    try {
      const response = await fetch(`${this.backendUrl}/api/live/session/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}` // User's auth token
        },
        body: JSON.stringify(config)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start session');
      }

      const token: SessionToken = await response.json();
      this.currentToken = token;
      
      // Schedule token refresh before expiration
      this.scheduleTokenRefresh(token);
      
      return token;
    } catch (error) {
      console.error('Error starting session:', error);
      throw error;
    }
  }

  /**
   * Stop current session
   */
  async stopSession(): Promise<void> {
    if (!this.currentToken) {
      return;
    }

    try {
      await fetch(`${this.backendUrl}/api/live/session/${this.currentToken.sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
    } catch (error) {
      console.error('Error stopping session:', error);
    } finally {
      this.clearTokenRefresh();
      this.currentToken = null;
    }
  }

  /**
   * Execute a critical tool call on the backend
   * This keeps sensitive operations server-side
   */
  async executeToolCall(toolName: string, args: any): Promise<any> {
    if (!this.currentToken) {
      throw new Error('No active session');
    }

    try {
      const response = await fetch(`${this.backendUrl}/api/live/tool/call`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'X-Session-Token': this.currentToken.token
        },
        body: JSON.stringify({
          sessionId: this.currentToken.sessionId,
          toolName,
          args
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Tool call failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Error executing tool call:', error);
      throw error;
    }
  }

  /**
   * Get current session token
   */
  getCurrentToken(): SessionToken | null {
    return this.currentToken;
  }

  /**
   * Check if session is valid
   */
  isSessionValid(): boolean {
    if (!this.currentToken) {
      return false;
    }
    return new Date() < this.currentToken.expiresAt;
  }

  /**
   * Get user's authentication token from storage
   */
  private getAuthToken(): string {
    // Get from localStorage or your auth context
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('User not authenticated');
    }
    return token;
  }

  /**
   * Schedule token refresh before expiration
   */
  private scheduleTokenRefresh(token: SessionToken): void {
    this.clearTokenRefresh();
    
    const expiresIn = token.expiresAt.getTime() - Date.now();
    const refreshAt = expiresIn - (5 * 60 * 1000); // Refresh 5 minutes before expiry
    
    if (refreshAt > 0) {
      this.tokenRefreshTimer = setTimeout(() => {
        this.refreshToken();
      }, refreshAt);
    }
  }

  /**
   * Refresh session token
   */
  private async refreshToken(): Promise<void> {
    if (!this.currentToken) {
      return;
    }

    try {
      const response = await fetch(`${this.backendUrl}/api/live/session/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({ sessionId: this.currentToken.sessionId })
      });

      if (response.ok) {
        const newToken: SessionToken = await response.json();
        this.currentToken = newToken;
        this.scheduleTokenRefresh(newToken);
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
    }
  }

  /**
   * Clear token refresh timer
   */
  private clearTokenRefresh(): void {
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
      this.tokenRefreshTimer = null;
    }
  }
}
