import type { TabContext } from './types'

const NO_TAB: TabContext = { url: null, title: null }

/**
 * Read the URL of the tab the user currently has open, using chrome.tabs.query.
 * Returns nulls when there is no accessible page (chrome:// pages, the new tab
 * page, or when running outside an extension context during `npm run dev`).
 */
export async function getActiveTab(): Promise<TabContext> {
  if (typeof chrome === 'undefined' || !chrome.tabs?.query) {
    return NO_TAB
  }

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
    const url = tab?.url ?? null

    if (!url || !/^https?:\/\//i.test(url)) {
      return { url: null, title: tab?.title ?? null }
    }

    return { url, title: tab?.title ?? null }
  } catch {
    return NO_TAB
  }
}

/** Short display form of a URL, e.g. "en.wikipedia.org". */
export function hostOf(url: string | null): string {
  if (!url) return ''
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}
