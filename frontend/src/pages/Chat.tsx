import { useState, useEffect, useRef } from 'react';
import { Send, Terminal, Bot, User, Trash2, History, X, ChevronDown, ChevronRight, Globe, Mail, Calendar, MessageSquare, Zap, Shield, Target, Sparkles, Monitor, MousePointer2, Keyboard, AlertCircle, Camera, Square } from 'lucide-react';
import { cn } from '../lib/utils';
import { useTranslation } from '../i18n';
import { MailView } from './MailView';
import { CalendarView } from './CalendarView';

type ChatMode = 'auto' | 'fast' | 'governed' | 'mission';

type RoninAttachment =
  | { type: 'screenshot'; url: string; description: string }
  | { type: 'action'; action: string; detail: string };

interface Message {
  role: 'user' | 'shogun';
  content: string;
  timestamp: string;
  model?: string;
  provider?: string;
  search?: boolean;
  mode?: ChatMode;
  attachments?: RoninAttachment[];
}

interface Session {
  id: string;
  startedAt: string;
  messages: Message[];
}

const STORAGE_KEY = 'shogun_comms_current';
const HISTORY_KEY = 'shogun_comms_history';
const MAX_HISTORY_SESSIONS = 50;

const WELCOME_KEY = 'chat.welcome_message';

function loadCurrent(t: any): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [{
      role: 'shogun',
      content: t(WELCOME_KEY),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }];
  } catch {
    return [{
      role: 'shogun',
      content: t(WELCOME_KEY),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }];
  }
}

function saveCurrent(msgs: Message[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(msgs));
}

function loadHistory(): Session[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function archiveSession(msgs: Message[], t: any) {
  const welcomeText = t(WELCOME_KEY);
  const real = msgs.filter(m => !(m.role === 'shogun' && m.content === welcomeText));
  if (real.length === 0) return;

  const history = loadHistory();
  const session: Session = {
    id: Date.now().toString(),
    startedAt: msgs[0]?.timestamp || new Date().toLocaleTimeString(),
    messages: msgs,
  };
  const updated = [session, ...history].slice(0, MAX_HISTORY_SESSIONS);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
}

export const ChatConsole = () => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>(() => loadCurrent(t));
  const operatorName = localStorage.getItem('shogun_operator_name') || 'Daimyo';
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [statusText, setStatusText] = useState<string | null>(null);
  const [chatMode, setChatMode] = useState<ChatMode>('auto');
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<Session[]>(loadHistory);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Persist messages to localStorage on every change
  useEffect(() => {
    saveCurrent(messages);
  }, [messages]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const handleSend = async () => {
    if (!input.trim() || isThinking) return;

    const userMsg: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput('');
    setIsThinking(true);
    setStatusText(null);

    const hist = updatedMessages
      .filter(m => m.role === 'user' || m.role === 'shogun')
      .slice(-20)
      .map(m => ({ role: m.role === 'shogun' ? 'assistant' : 'user', content: m.content }));

    const placeholder: Message = {
      role: 'shogun',
      content: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, placeholder]);

    try {
      const controller = new AbortController();
      abortRef.current = controller;
      const resp = await fetch('/api/v1/agents/shogun/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, history: hist.slice(0, -1), mode: chatMode }),
        signal: controller.signal,
      });

      if (!resp.ok || !resp.body) throw new Error(`HTTP ${resp.status}`);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let assembled = '';
      let meta: { model?: string; provider?: string; timestamp?: string; search?: boolean; mode?: ChatMode } = {};

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const raw = line.slice(6).trim();
          if (raw === '[DONE]') break;

          try {
            const evt = JSON.parse(raw);

            if (evt.type === 'meta') {
              meta = { 
                model: evt.model, 
                provider: evt.provider, 
                timestamp: evt.timestamp,
                search: evt.search,
                mode: evt.mode,
              };
              setMessages(prev => {
                const copy = [...prev];
                copy[copy.length - 1] = { ...copy[copy.length - 1], ...meta };
                return copy;
              });
            } else if (evt.type === 'status') {
              setStatusText(evt.content);
            } else if (evt.type === 'token') {
              setIsThinking(false);
              setStatusText(null);
              assembled += evt.content;
              const snap = assembled;
              setMessages(prev => {
                const copy = [...prev];
                copy[copy.length - 1] = { ...copy[copy.length - 1], content: snap };
                return copy;
              });
            } else if (evt.type === 'error') {
              setMessages(prev => {
                const copy = [...prev];
                copy[copy.length - 1] = { ...copy[copy.length - 1], content: evt.content };
                return copy;
              });
            } else if (evt.type === 'ronin_screenshot') {
              setMessages(prev => {
                const copy = [...prev];
                const last = copy[copy.length - 1];
                const existing = last.attachments || [];
                copy[copy.length - 1] = {
                  ...last,
                  attachments: [...existing, { type: 'screenshot', url: evt.url, description: evt.description || 'Desktop screenshot' }],
                };
                return copy;
              });
            } else if (evt.type === 'ronin_action') {
              setMessages(prev => {
                const copy = [...prev];
                const last = copy[copy.length - 1];
                const existing = last.attachments || [];
                copy[copy.length - 1] = {
                  ...last,
                  attachments: [...existing, { type: 'action', action: evt.action, detail: evt.detail || '' }],
                };
                return copy;
              });
            } else if (evt.type === 'action') {
              setStatusText(evt.content);
            }
          } catch { /* malformed event */ }
        }
      }
    } catch (err: any) {
      if (err?.name === 'AbortError') {
        // User cancelled — mark the message as cancelled
        setMessages(prev => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last.content === '') {
            copy[copy.length - 1] = { ...last, content: '⛔ Cancelled by operator.' };
          } else {
            copy[copy.length - 1] = { ...last, content: last.content + '\n\n⛔ *Cancelled by operator.*' };
          }
          return copy;
        });
      } else {
        console.error('Streaming failed:', err);
        setMessages(prev => {
          const copy = [...prev];
          copy[copy.length - 1] = {
            ...copy[copy.length - 1],
            content: '⚠️ ' + t('chat.bridge_interrupted', 'Neural bridge interrupted. Check logs.'),
          };
          return copy;
        });
      }
    } finally {
      abortRef.current = null;
      setIsThinking(false);
      setStatusText(null);
    }
  };

  const handleCancel = () => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  };

  const handleClear = () => {
    archiveSession(messages, t);
    const fresh: Message[] = [{ 
      role: 'shogun',
      content: t(WELCOME_KEY),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    }];
    setMessages(fresh);
    setHistory(loadHistory());
  };

  const openHistory = () => {
    setHistory(loadHistory());
    setShowHistory(true);
  };

  const restoreSession = (session: Session) => {
    archiveSession(messages, t);
    setMessages(session.messages);
    setShowHistory(false);
  };

  return (
    <div className="flex flex-col w-full min-w-0 h-full space-y-4">
      {/* Clear Bar */}
      <div className="flex justify-between items-center shrink-0">
        <span className="text-xs font-bold text-shogun-subdued uppercase tracking-widest">
          {t('chat.neural_link', 'Neural Connection')}
        </span>
        <button
          onClick={handleClear}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-red-500/20 text-red-400/80 hover:text-red-400 hover:bg-red-500/10 rounded-lg text-xs font-bold transition-all"
          title={t('chat.clear_tooltip', 'Clear current session')}
        >
          <Trash2 className="w-3.5 h-3.5" />
          {t('chat.clear_session', 'Clear Link')}
        </button>
      </div>

      {/* Chat area */}
      <div className="flex-1 w-full shogun-card overflow-hidden flex flex-col p-0">
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide scroll-smooth"
        >
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-shogun-subdued space-y-3 opacity-50">
              <Terminal className="w-12 h-12" />
              <p className="text-sm italic tracking-wide">{t('chat.terminal_empty', 'Terminal empty. Awaiting mission parameters.')}</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                'flex gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300',
                msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
              )}
            >
              <div
                className={cn(
                  'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border',
                  msg.role === 'user'
                    ? 'bg-shogun-blue/10 border-shogun-blue/30 text-shogun-blue'
                    : 'bg-shogun-gold/10 border-shogun-gold/30 text-shogun-gold'
                )}
              >
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={cn(
                  'max-w-[70%] space-y-1 flex flex-col',
                  msg.role === 'user' ? 'items-end' : 'items-start'
                )}
              >
                <div
                  className={cn(
                    'p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap',
                    msg.role === 'user'
                      ? 'bg-shogun-card border border-shogun-border text-shogun-text rounded-tr-none'
                      : 'bg-[#050508] border border-shogun-border text-shogun-gold rounded-tl-none font-mono'
                  )}
                >
                  {msg.role === 'shogun' && msg.content === '' && (!msg.attachments || msg.attachments.length === 0) ? (
                    <div className="flex items-center gap-2 py-1">
                      {statusText ? (
                        <>
                          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                          <span className="text-xs text-cyan-400/80 font-mono animate-pulse">{statusText}</span>
                        </>
                      ) : (
                        <>
                          <span className="w-2 h-2 rounded-full bg-shogun-gold/70 animate-bounce [animation-delay:0ms]" />
                          <span className="w-2 h-2 rounded-full bg-shogun-gold/70 animate-bounce [animation-delay:150ms]" />
                          <span className="w-2 h-2 rounded-full bg-shogun-gold/70 animate-bounce [animation-delay:300ms]" />
                        </>
                      )}
                    </div>
                  ) : (
                    <>
                      {msg.content}
                      {/* ── Ronin Visual Feed ── */}
                      {msg.attachments && msg.attachments.length > 0 && (
                        <div className={cn("space-y-2", msg.content ? "mt-3 border-t border-shogun-border/30 pt-3" : "")}>
                          {msg.attachments.map((att, idx) => {
                            if (att.type === 'screenshot') {
                              return (
                                <div key={idx} className="rounded-lg overflow-hidden border border-cyan-500/30 bg-black/40">
                                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-500/10 border-b border-cyan-500/20">
                                    <Camera className="w-3 h-3 text-cyan-400" />
                                    <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">Desktop Screenshot</span>
                                  </div>
                                  <img
                                    src={att.url}
                                    alt={att.description}
                                    className="w-full max-h-[400px] object-contain cursor-pointer hover:opacity-90 transition-opacity"
                                    onClick={() => window.open(att.url, '_blank')}
                                  />
                                </div>
                              );
                            }
                            if (att.type === 'action') {
                              const isClick = att.action === 'click';
                              const isType = att.action === 'type';
                              const isError = att.action === 'error';
                              return (
                                <div
                                  key={idx}
                                  className={cn(
                                    'flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono border',
                                    isError
                                      ? 'bg-red-500/10 border-red-500/30 text-red-400'
                                      : isClick
                                        ? 'bg-purple-500/10 border-purple-500/30 text-purple-300'
                                        : isType
                                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                                          : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
                                  )}
                                >
                                  {isClick && <MousePointer2 className="w-3.5 h-3.5 shrink-0" />}
                                  {isType && <Keyboard className="w-3.5 h-3.5 shrink-0" />}
                                  {isError && <AlertCircle className="w-3.5 h-3.5 shrink-0" />}
                                  {!isClick && !isType && !isError && <Monitor className="w-3.5 h-3.5 shrink-0" />}
                                  <span>{att.detail}</span>
                                </div>
                              );
                            }
                            return null;
                          })}
                          {/* Progress indicator while tools are still executing */}
                          {isThinking && statusText && (
                            <div className="flex items-center gap-2 px-3 py-2 text-xs text-cyan-400/70 font-mono">
                              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                              <span className="animate-pulse">{statusText}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
                <div className="flex items-center gap-2 px-1 mt-1">
                  <span className="text-[10px] text-shogun-subdued font-bold tracking-wider">{msg.role === 'user' ? operatorName : t('chat.agent_label', 'SHOGUN')}</span>
                  <span className="text-[10px] text-shogun-subdued opacity-50">{msg.timestamp}</span>
                  {msg.role === 'shogun' && (msg.model || msg.search || msg.mode) && (
                    <div className="flex items-center gap-1.5">
                      {msg.mode && (
                        <div className={cn(
                          "flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                          msg.mode === 'fast'
                            ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-400"
                            : msg.mode === 'governed'
                              ? "bg-amber-500/10 border border-amber-500/30 text-amber-400"
                              : "bg-purple-500/10 border border-purple-500/30 text-purple-400"
                        )}>
                          {msg.mode === 'fast' ? <Zap className="w-2.5 h-2.5" /> : msg.mode === 'governed' ? <Shield className="w-2.5 h-2.5" /> : <Target className="w-2.5 h-2.5" />}
                          {msg.mode === 'fast' ? 'Fast' : msg.mode === 'governed' ? 'Governed' : 'Mission'}
                        </div>
                      )}
                      {msg.search ? (
                        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-shogun-blue/10 border border-shogun-blue/30 text-shogun-blue">
                          <Globe className="w-2.5 h-2.5" />
                          {t('chat.web_search', 'Web Search')}
                        </div>
                      ) : msg.model ? (
                        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-shogun-card border border-shogun-border text-shogun-subdued">
                          <Bot className="w-2.5 h-2.5" />
                          {msg.model}
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Input bar */}
        <div className="p-4 bg-[#050508]/50 border-t border-shogun-border shrink-0">
          {/* Mode selector */}
          <div className="flex items-center gap-1 mb-3">
            {([
              { id: 'auto' as ChatMode, label: 'Auto', icon: Sparkles, color: 'cyan', desc: 'Automatically selects the best mode' },
              { id: 'fast' as ChatMode, label: 'Fast Chat', icon: Zap, color: 'emerald', desc: 'Conversation only — no tools or memory' },
              { id: 'governed' as ChatMode, label: 'Governed', icon: Shield, color: 'amber', desc: 'Context-aware with memory (coming soon)' },
              { id: 'mission' as ChatMode, label: 'Mission', icon: Target, color: 'purple', desc: 'Full agent orchestration with tools' },
            ]).map(({ id, label, icon: Icon, color }) => (
              <button
                key={id}
                type="button"
                onClick={() => setChatMode(id)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest border transition-all",
                  chatMode === id
                    ? `bg-${color}-500/15 border-${color}-500/40 text-${color}-400`
                    : "bg-transparent border-shogun-border/50 text-shogun-subdued/60 hover:border-shogun-subdued hover:text-shogun-subdued"
                )}
                style={chatMode === id ? {
                  backgroundColor: color === 'cyan' ? 'rgba(6,182,212,0.15)' : color === 'emerald' ? 'rgba(16,185,129,0.15)' : color === 'amber' ? 'rgba(245,158,11,0.15)' : 'rgba(168,85,247,0.15)',
                  borderColor: color === 'cyan' ? 'rgba(6,182,212,0.4)' : color === 'emerald' ? 'rgba(16,185,129,0.4)' : color === 'amber' ? 'rgba(245,158,11,0.4)' : 'rgba(168,85,247,0.4)',
                  color: color === 'cyan' ? 'rgb(34,211,238)' : color === 'emerald' ? 'rgb(52,211,153)' : color === 'amber' ? 'rgb(251,191,36)' : 'rgb(192,132,252)',
                } : {}}
              >
                <Icon className="w-3 h-3" />
                {label}
              </button>
            ))}
          </div>

          <div className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
              disabled={isThinking}
              placeholder={isThinking ? t('chat.placeholder_thinking', 'Shogun is thinking...') : chatMode === 'auto' ? 'Ask anything — Shogun routes automatically...' : chatMode === 'fast' ? 'Ask anything...' : chatMode === 'mission' ? 'Enter mission directive...' : 'Ask with context...'}
              className="w-full bg-shogun-card border border-shogun-border rounded-xl py-4 pl-6 pr-14 text-shogun-text placeholder:text-shogun-subdued focus:outline-none focus:border-shogun-blue focus:ring-1 focus:ring-shogun-blue/20 transition-all font-mono text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            />
            {isThinking ? (
              <button
                onClick={handleCancel}
                className="absolute right-2 p-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-all active:scale-95 animate-pulse"
                title="Cancel operation"
              >
                <Square className="w-5 h-5 fill-current" />
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="absolute right-2 p-2 bg-shogun-blue text-white rounded-lg hover:bg-shogun-blue/80 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            )}
          </div>
          <div className="flex justify-between mt-3 px-2">
            <div className="flex gap-4">
              <span className="text-[10px] text-shogun-subdued flex items-center gap-1">
                <Terminal className="w-3 h-3" /> UTF-8
              </span>
              <button
                onClick={openHistory}
                className="text-[10px] text-shogun-subdued flex items-center gap-1 underline cursor-pointer hover:text-shogun-blue transition-colors"
              >
                <History className="w-3 h-3" />
                {t('chat.view_history', 'View History')} ({history.length} {t('chat.sessions', 'sessions')})
              </button>
            </div>
            <span className="text-[10px] text-shogun-subdued italic">{t('chat.enter_to_send', 'Press Enter to send')}</span>
          </div>
        </div>
      </div>

      {/* ── History Drawer ─────────────────────────────────────── */}
      {showHistory && (
        <div className="fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowHistory(false)}
          />

          <div className="absolute right-0 top-0 h-full w-full max-w-xl bg-shogun-bg border-l border-shogun-border flex flex-col shadow-2xl">
            <div className="flex items-center justify-between p-5 border-b border-shogun-border shrink-0">
              <div>
                <h3 className="text-lg font-bold text-shogun-text flex items-center gap-2">
                  <History className="w-5 h-5 text-shogun-gold" />
                  {t('chat.comms_history', 'Comms History')}
                </h3>
                <p className="text-[11px] text-shogun-subdued mt-0.5">
                  {history.length} {t('chat.archived_sessions', 'archived sessions')}
                </p>
              </div>
              <button
                onClick={() => setShowHistory(false)}
                className="p-2 text-shogun-subdued hover:text-shogun-text hover:bg-shogun-card rounded-lg transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {history.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-shogun-subdued space-y-3 opacity-50">
                  <History className="w-10 h-10" />
                  <p className="text-sm italic">{t('chat.no_history', 'No archived sessions found.')}</p>
                </div>
              ) : (
                history.map(session => {
                  const isExpanded = expandedSession === session.id;
                  const preview = session.messages.find(m => m.role === 'user')?.content || '(empty)';
                  const msgCount = session.messages.filter(m => m.role === 'user').length;
                  return (
                    <div key={session.id} className="border border-shogun-border rounded-xl overflow-hidden">
                      <div
                        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-shogun-card/50 transition-colors"
                        onClick={() => setExpandedSession(isExpanded ? null : session.id)}
                      >
                        {isExpanded
                          ? <ChevronDown className="w-4 h-4 text-shogun-subdued shrink-0" />
                          : <ChevronRight className="w-4 h-4 text-shogun-subdued shrink-0" />
                        }
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-mono text-shogun-text truncate">{preview}</p>
                          <p className="text-[10px] text-shogun-subdued mt-0.5">
                            {session.startedAt} · {msgCount} {t('chat.messages', 'messages')}
                          </p>
                        </div>
                        <button
                          onClick={e => { e.stopPropagation(); restoreSession(session); }}
                          className="text-[10px] text-shogun-blue hover:text-shogun-gold font-bold uppercase tracking-wider shrink-0 px-2 py-1 border border-shogun-blue/30 rounded-lg transition-colors"
                        >
                          {t('chat.restore', 'RESTORE')}
                        </button>
                      </div>

                      {isExpanded && (
                        <div className="border-t border-shogun-border bg-[#050508] p-3 space-y-2 max-h-64 overflow-y-auto">
                          {session.messages.map((m, i) => (
                            <div key={i} className={cn('text-xs', m.role === 'user' ? 'text-right' : 'text-left')}>
                              <span className={cn(
                                'inline-block px-3 py-1.5 rounded-lg max-w-[85%] text-left',
                                m.role === 'user'
                                  ? 'bg-shogun-blue/10 text-shogun-text border border-shogun-blue/20'
                                  : 'bg-shogun-gold/5 text-shogun-gold border border-shogun-gold/10 font-mono'
                              )}>
                                {m.content.length > 120 ? m.content.slice(0, 120) + '…' : m.content}
                              </span>
                              <div className="text-[9px] text-shogun-subdued mt-0.5 px-1">{m.timestamp}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>

            {history.length > 0 && (
              <div className="p-4 border-t border-shogun-border shrink-0">
                <button
                  onClick={() => {
                    localStorage.removeItem(HISTORY_KEY);
                    setHistory([]);
                  }}
                  className="w-full text-xs text-red-400/60 hover:text-red-400 transition-colors py-2 border border-red-400/10 hover:border-red-400/30 rounded-lg"
                >
                  {t('chat.clear_all_history', 'CLEAR ALL HISTORY')}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export const Chat = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'chat' | 'mail' | 'calendar'>('chat');

  return (
    <div className="flex flex-col w-full min-w-0 h-[calc(100vh-140px)] space-y-4">
      {/* Overall Header */}
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h2 className="text-3xl font-bold shogun-title flex items-center gap-3">
            {t('chat.title', 'Comms')}{' '}
            <span className="text-xs font-normal text-shogun-subdued bg-shogun-card px-2 py-1 rounded border border-shogun-border tracking-[0.2em] uppercase">
              {activeTab === 'chat' && t('chat.badge', 'Command Console')}
              {activeTab === 'mail' && t('mail.badge', 'Mail Client')}
              {activeTab === 'calendar' && t('calendar.badge', 'Calendar Board')}
            </span>
          </h2>
          <p className="text-shogun-subdued text-sm mt-1">{t('comms.subtitle', 'Chat · Mail · Calendar')}</p>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex border-b border-shogun-border shrink-0">
        {([
          { id: 'chat', label: t('chat.tab_chat', 'Chat'), icon: MessageSquare },
          { id: 'mail', label: t('chat.tab_mail', 'Mail'), icon: Mail },
          { id: 'calendar', label: t('chat.tab_calendar', 'Calendar'), icon: Calendar }
        ] as const).map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              "px-6 py-3 text-sm font-bold uppercase tracking-widest transition-all relative flex items-center gap-2",
              activeTab === id ? "text-shogun-blue" : "text-shogun-subdued hover:text-shogun-text"
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
            {activeTab === id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-shogun-blue shadow-[0_0_10px_rgba(74,140,199,0.5)]" />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content Panel */}
      <div className="flex-1 min-h-0">
        {activeTab === 'chat' && <ChatConsole />}
        {activeTab === 'mail' && <MailView />}
        {activeTab === 'calendar' && <CalendarView />}
      </div>
    </div>
  );
};

