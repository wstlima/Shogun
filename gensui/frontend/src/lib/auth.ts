export function getToken(): string | null {
  return localStorage.getItem('gensui_token');
}

export function getAdmin(): Record<string, string> | null {
  const raw = localStorage.getItem('gensui_admin');
  return raw ? JSON.parse(raw) : null;
}

export function setAuth(token: string, admin: Record<string, string>): void {
  localStorage.setItem('gensui_token', token);
  localStorage.setItem('gensui_admin', JSON.stringify(admin));
}

export function clearAuth(): void {
  localStorage.removeItem('gensui_token');
  localStorage.removeItem('gensui_admin');
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
