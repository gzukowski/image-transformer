export type UploadStatus = 'pending' | 'processing' | 'done' | 'failed'

export interface Upload {
    id: string
    filename: string
    status: UploadStatus
    thumbnail_url: string | null
    created_at: string
}

const API_BASE = '/api'

export async function listUploads(): Promise<Upload[]> {
    const response = await fetch(`${API_BASE}/uploads`)
    if (!response.ok) throw new Error('Failed to load uploads')
    const data: { uploads: Upload[] } = await response.json()
    return data.uploads
}

export async function uploadFile(file: File): Promise<Upload> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/uploads`, {
        method: 'POST',
        body: formData,
    })
    if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(body?.detail ?? 'Upload failed')
    }
    return response.json()
}

export function thumbnailUrl(id: string): string {
    return `${API_BASE}/uploads/${id}/thumbnail`
}
