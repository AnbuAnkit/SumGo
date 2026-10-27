import type { ChatRequestBody, ChatResponseBody } from './types'

const API_BASE: string =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? 'http://localhost:8000'

/** Send the conversation plus the active tab context to the FastAPI agent. */
export async function sendChat(body: ChatRequestBody): Promise<ChatResponseBody> {
  let response: Response

  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new Error(
      `Could not reach the backend at ${API_BASE}. Is the FastAPI server running?`,
    )
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}.`)
  }

  return (await response.json()) as ChatResponseBody
}
