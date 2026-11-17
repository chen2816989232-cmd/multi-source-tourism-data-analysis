// In production use the address from which this page was opened.
// VITE_API_BASE_URL can still override it for local development.
export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''
export const schemaname = 'lvxing2f63wq5x'
export const isPreviewEnv = !import.meta.env.DEV && !apiBaseUrl
export const fileUploadUrl = '/lvxing2f63wq5x/file/upload'
const base = {
  get() {
    const origin = apiBaseUrl || window.location.origin
    return {
      url: origin + '/lvxing2f63wq5x/',
      name: 'lvxing2f63wq5x',
    }
  },
}
export default base
