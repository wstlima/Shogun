export class ShogunClient {
  constructor(
    private readonly baseUrl = process.env.SHOGUN_INTERNAL_API_URL || 'http://127.0.0.1:8000',
    private readonly apiKey = process.env.SHOGUN_INTERNAL_API_KEY || '',
  ) {}

  async dispatch(commandEnvelope: unknown): Promise<any> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15_000);
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/katana/command/dispatch`, {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          ...(this.apiKey ? { authorization: `Bearer ${this.apiKey}` } : {}),
        },
        body: JSON.stringify(commandEnvelope),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Shogun returned HTTP ${response.status}`);
      const payload = await response.json() as any;
      return payload.data?.response_envelope;
    } finally {
      clearTimeout(timeout);
    }
  }
}
