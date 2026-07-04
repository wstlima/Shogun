import test from 'node:test';
import assert from 'node:assert/strict';
import { stripMention, toCommandEnvelope } from '../src/normalize.js';

test('strips Teams HTML and plain mentions', () => {
  assert.equal(stripMention('<at>Shogun</at> status'), 'status');
  assert.equal(stripMention('@Shogun: show agents'), 'show agents');
});

test('normalizes a channel activity', () => {
  const envelope = toCommandEnvelope({
    id: 'm1', text: '<at>Shogun</at> status', channelId: 'msteams',
    conversation: { id: 'conversation-1', conversationType: 'channel', tenantId: 'tenant-1' },
    channelData: { team: { id: 'team-1' }, channel: { id: 'channel-1' } },
    from: { id: 'teams-user-1', aadObjectId: 'aad-1', name: 'Michael' },
  });
  assert.equal(envelope.normalized_text, 'status');
  assert.equal(envelope.conversation_type, 'channel');
  assert.equal(envelope.tenant_id, 'tenant-1');
});
