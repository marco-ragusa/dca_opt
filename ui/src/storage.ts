import type { Asset, Settings } from './types';

const KEYS = {
  settings: 'dca_opt_settings',
  assets: 'dca_opt_assets',
  landingCollapsed: 'dca_opt_landing_collapsed',
} as const;

export const DEFAULT_SETTINGS: Settings = {
  increment: 1000,
  onlyBuy: true,
  optimalRedistribute: false,
};

function tryParse<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function loadSettings(): Settings {
  return { ...DEFAULT_SETTINGS, ...tryParse<Partial<Settings>>(KEYS.settings, {}) };
}

export function loadAssets(): Asset[] {
  const val = tryParse<unknown>(KEYS.assets, null);
  return Array.isArray(val) ? (val as Asset[]) : [];
}

export function loadLandingCollapsed(): boolean {
  return tryParse<boolean>(KEYS.landingCollapsed, false);
}

export function saveSettings(s: Settings): void {
  localStorage.setItem(KEYS.settings, JSON.stringify(s));
}

export function saveAssets(a: Asset[]): void {
  localStorage.setItem(KEYS.assets, JSON.stringify(a));
}

export function saveLandingCollapsed(v: boolean): void {
  localStorage.setItem(KEYS.landingCollapsed, JSON.stringify(v));
}
