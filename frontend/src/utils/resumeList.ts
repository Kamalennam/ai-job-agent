import type { Resume } from '@/types/resume'

/** Merge a server list with resumes the screen already shows.

A slower list request must not hide a file that upload just saved, and a
stale snapshot must not roll parse progress backwards.
*/
export function applyResumeList(serverItems: Resume[], localItems: Resume[]): Resume[] {
  const serverIds = new Set(serverItems.map((item) => item.id))
  const localOnly = localItems.filter((item) => !serverIds.has(item.id))
  const localById = new Map(localItems.map((item) => [item.id, item]))

  const merged = serverItems.map((item) => {
    const local = localById.get(item.id)
    if (!local || local.parse_progress <= item.parse_progress) {
      return item
    }
    return {
      ...item,
      status: local.status,
      parse_progress: local.parse_progress,
      parse_stage: local.parse_stage,
    }
  })

  return [...localOnly, ...merged]
}
