import { AgentApplication, MemoryStorage, TurnState } from '@microsoft/agents-hosting';
import { startServer } from '@microsoft/agents-hosting-express';
import type { Request, Response } from 'express';
import { ShogunClient } from './shogun-client.js';
import { toCommandEnvelope } from './normalize.js';

const client = new ShogunClient();

class ShogunTeamsAgent extends AgentApplication<TurnState> {
  constructor(storage: MemoryStorage) {
    super({ storage, proactive: { storage } });
    this.onConversationUpdate('membersAdded', async (context: any) => {
      await this.proactive.storeConversation(context);
      await context.sendActivity('Shogun is connected. Type “help” to see commands available to your role.');
    });
    this.onActivity('message', async (context: any) => {
      const correlationId = context.activity?.id || 'unknown';
      try {
        await this.proactive.storeConversation(context);
        const response = await client.dispatch(toCommandEnvelope(context.activity));
        if (!response) throw new Error('Shogun returned no response envelope');
        if (response.card_payload && Object.keys(response.card_payload).length) {
          await context.sendActivity({
            type: 'message',
            text: response.text,
            attachments: [{
              contentType: 'application/vnd.microsoft.card.adaptive',
              content: response.card_payload,
            }],
          });
        } else {
          await context.sendActivity(response.text);
        }
      } catch (error) {
        console.error(JSON.stringify({ event: 'dispatch_failed', correlationId, error: String(error) }));
        await context.sendActivity(
          `Shogun is currently unreachable. The Teams Bridge is online, but the backend did not respond.\nCorrelation ID: ${correlationId}`,
        );
      }
    });
    this.onActivity('invoke', async (context: any) => {
      const value = context.activity?.value || {};
      if (!['approve', 'reject'].includes(value.action) || !value.request_id) {
        await context.sendActivity('This card action is not valid.');
        return;
      }
      const activity = { ...context.activity, text: `${value.action} ${value.request_id}`, attachments: [] };
      const response = await client.dispatch(toCommandEnvelope(activity));
      await context.sendActivity(response.text);
    });
  }
}

const agent = new ShogunTeamsAgent(new MemoryStorage());
startServer(agent, {
  rateLimitOptions: { windowMs: 60_000, max: 120 },
  beforeListen: app => {
    app.get(['/api/teams/health', '/api/teams/version'], (_request: Request, response: Response) => {
      response.json({ service: 'shogun-teams-bridge', status: 'ok', version: '1.0.0' });
    });
    app.post('/api/teams/proactive', async (request: Request, response: Response) => {
      const configuredKey = process.env.SHOGUN_INTERNAL_API_KEY;
      if (!configuredKey || request.headers.authorization !== `Bearer ${configuredKey}`) {
        response.status(401).json({ error: 'unauthorized' });
        return;
      }
      const { conversation_id: conversationId, text, card_payload: cardPayload } = request.body || {};
      if (!conversationId || !text) {
        response.status(422).json({ error: 'conversation_id and text are required' });
        return;
      }
      try {
        const activity: any = cardPayload
          ? {
              type: 'message',
              text,
              attachments: [{
                contentType: 'application/vnd.microsoft.card.adaptive',
                content: cardPayload,
              }],
            }
          : { type: 'message', text };
        const result = await agent.proactive.sendActivity(agent.adapter, conversationId, activity);
        response.json({ ok: true, activity_id: result.id });
      } catch (error) {
        response.status(502).json({ ok: false, error: String(error) });
      }
    });
  },
});
