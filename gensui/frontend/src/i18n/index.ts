/**
 * Gensui i18n — Internationalization system.
 *
 * Same pattern as Shogun: React context + hook, lazy-loaded JSON packs.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';

// ── Types ────────────────────────────────────────────────────

export interface LanguageMeta {
  code: string;
  name: string;        // Native name
  englishName: string;
  flag: string;
}

type TranslationMap = Record<string, string | Record<string, string | Record<string, string>>>;

interface I18nContextType {
  language: string;
  setLanguage: (code: string) => void;
  t: (key: string, fallback?: string) => string;
  languages: LanguageMeta[];
  loading: boolean;
}

// ── Available Languages ──────────────────────────────────────

export const AVAILABLE_LANGUAGES: LanguageMeta[] = [
  { code: 'en', name: 'English',    englishName: 'English',    flag: '🇬🇧' },
  { code: 'de', name: 'Deutsch',    englishName: 'German',     flag: '🇩🇪' },
  { code: 'it', name: 'Italiano',   englishName: 'Italian',    flag: '🇮🇹' },
  { code: 'fr', name: 'Français',   englishName: 'French',     flag: '🇫🇷' },
  { code: 'es', name: 'Español',    englishName: 'Spanish',    flag: '🇪🇸' },
  { code: 'pt', name: 'Português',  englishName: 'Portuguese', flag: '🇵🇹' },
  { code: 'pl', name: 'Polski',     englishName: 'Polish',     flag: '🇵🇱' },
  { code: 'da', name: 'Dansk',      englishName: 'Danish',     flag: '🇩🇰' },
  { code: 'no', name: 'Norsk',      englishName: 'Norwegian',  flag: '🇳🇴' },
  { code: 'sv', name: 'Svenska',    englishName: 'Swedish',    flag: '🇸🇪' },
  { code: 'uk', name: 'Українська', englishName: 'Ukrainian',  flag: '🇺🇦' },
  { code: 'zh', name: '中文',       englishName: 'Chinese',    flag: '🇨🇳' },
  { code: 'ja', name: '日本語',     englishName: 'Japanese',   flag: '🇯🇵' },
  { code: 'ko', name: '한국어',     englishName: 'Korean',     flag: '🇰🇷' },
];

// ── Pack cache + loader ──────────────────────────────────────

const packCache: Record<string, TranslationMap> = {};
const packModules = import.meta.glob('./*.json', { eager: false }) as Record<string, () => Promise<{ default: TranslationMap }>>;

async function loadPack(code: string): Promise<TranslationMap> {
  if (packCache[code]) return packCache[code];
  const key = `./${code}.json`;
  const loader = packModules[key];
  if (!loader) {
    console.warn(`[gensui-i18n] Pack not found: ${code}, falling back to English`);
    if (code !== 'en') return loadPack('en');
    return {};
  }
  try {
    const mod = await loader();
    packCache[code] = mod.default;
    return mod.default;
  } catch (err) {
    console.error(`[gensui-i18n] Failed to load: ${code}`, err);
    if (code !== 'en') return loadPack('en');
    return {};
  }
}

// ── Deep key resolver ────────────────────────────────────────

function resolveKey(t: TranslationMap, key: string): string | undefined {
  const parts = key.split('.');
  let current: any = t;
  for (const part of parts) {
    if (current == null || typeof current !== 'object') return undefined;
    current = current[part];
  }
  return typeof current === 'string' ? current : undefined;
}

// ── Context ──────────────────────────────────────────────────

const I18nContext = createContext<I18nContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
  languages: AVAILABLE_LANGUAGES,
  loading: false,
});

// ── Provider ─────────────────────────────────────────────────

export const I18nProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState(() =>
    localStorage.getItem('gensui_language') || 'en'
  );
  const [translations, setTranslations] = useState<TranslationMap>({});
  const [englishFallback, setEnglishFallback] = useState<TranslationMap>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadPack('en').then(setEnglishFallback); }, []);
  useEffect(() => {
    setLoading(true);
    loadPack(language).then(pack => { setTranslations(pack); setLoading(false); });
  }, [language]);

  const setLanguage = useCallback((code: string) => {
    localStorage.setItem('gensui_language', code);
    setLanguageState(code);
  }, []);

  const t = useCallback((key: string, fallback?: string): string => {
    return resolveKey(translations, key)
      || resolveKey(englishFallback, key)
      || fallback
      || key.split('.').pop()
      || key;
  }, [translations, englishFallback]);

  return React.createElement(I18nContext.Provider, {
    value: { language, setLanguage, t, languages: AVAILABLE_LANGUAGES, loading },
  }, children);
};

// ── Hook ─────────────────────────────────────────────────────

export const useTranslation = (): I18nContextType => useContext(I18nContext);
