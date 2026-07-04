import { randomUUID } from 'node:crypto';

export type Activity = Record<string, any>;

export function stripMention(text: string): string {
  return text
    .replace(/<at\b[^>]*>.*?<\/at>/gis, ' ')
    .replace(/^\s*@(?:Shogun(?:\s+AFM)?)\b[:,]?\s*/i, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function toCommandEnvelope(activity: Activity) {
  const conversationType = activity.conversation?.conversationType === 'personal'
    ? 'personal'
    : activity.conversation?.conversationType === 'groupChat' ? 'groupchat' : 'channel';
  const rawText = String(activity.text || '');
  return {
    source: 'microsoft_teams',
    adapter_version: '1.0.0',
    correlation_id: randomUUID(),
    tenant_id: activity.conversation?.tenantId || activity.channelData?.tenant?.id || '',
    team_id: activity.channelData?.team?.id || null,
    channel_id: activity.channelData?.channel?.id || null,
    chat_id: conversationType !== 'channel' ? activity.conversation?.id || null : null,
    conversation_reference_id: activity.conversation?.id || null,
    conversation_type: conversationType,
    message_id: activity.id || randomUUID(),
    reply_to_id: activity.replyToId || null,
    user: {
      teams_user_id: activity.from?.id || '',
      aad_object_id: activity.from?.aadObjectId || null,
      display_name: activity.from?.name || 'Unknown Teams user',
      user_principal_name: activity.from?.userPrincipalName || null,
    },
    raw_text: rawText,
    normalized_text: stripMention(rawText),
    attachments: (activity.attachments || []).map((item: any) => ({
      content_type: item.contentType, name: item.name || null,
    })),
    received_at: new Date().toISOString(),
    service_url: activity.serviceUrl || null,
    conversation_reference: {
      activityId: activity.id,
      user: activity.from,
      bot: activity.recipient,
      conversation: activity.conversation,
      channelId: activity.channelId,
      serviceUrl: activity.serviceUrl,
    },
  };
}
