import { useCallback, useEffect, useRef, useState } from 'react'
import { listUploads, thumbnailUrl, uploadFile, type Upload } from './api'
import './App.css'

const POLL_INTERVAL_MS = 2000

function App() {
    const [uploads, setUploads] = useState<Upload[]>([])
    const [error, setError] = useState<string | null>(null)
    const [isUploading, setIsUploading] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const refresh = useCallback(async () => {
        try {
            setUploads(await listUploads())
            setError(null)
        } catch {
            setError('Could not reach the API')
        }
    }, [])

    useEffect(() => {
        refresh()
        const interval = setInterval(refresh, POLL_INTERVAL_MS)
        return () => clearInterval(interval)
    }, [refresh])

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        const file = fileInputRef.current?.files?.[0]
        if (!file) return

        setIsUploading(true)
        setError(null)
        try {
            await uploadFile(file)
            if (fileInputRef.current) fileInputRef.current.value = ''
            await refresh()
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Upload failed')
        } finally {
            setIsUploading(false)
        }
    }

    return (
        <main id="app">
            <h1>PicJob</h1>

            <form className="upload-form" onSubmit={handleSubmit}>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/png,image/jpeg,image/webp,image/gif"
                    required
                />
                <button type="submit" disabled={isUploading}>
                    {isUploading ? 'Uploading…' : 'Upload'}
                </button>
            </form>

            {error && <p className="error">{error}</p>}

            <ul className="uploads">
                {uploads.map((upload) => (
                    <li key={upload.id} className="upload-row">
                        <div className="thumb">
                            {upload.status === 'done' ? (
                                <img
                                    src={thumbnailUrl(upload.id)}
                                    alt={upload.filename}
                                />
                            ) : (
                                <span
                                    className={`status status-${upload.status}`}
                                >
                                    {upload.status}
                                </span>
                            )}
                        </div>
                        <span className="filename">{upload.filename}</span>
                    </li>
                ))}
            </ul>
        </main>
    )
}

export default App
