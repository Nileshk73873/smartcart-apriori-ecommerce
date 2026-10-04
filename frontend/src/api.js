import axios from 'axios'
import { API_URL } from './config'

const api = axios.create({
  baseURL: API_URL,
})

api.interceptors.request.use(
  (config) => {
    try {
      const stored = localStorage.getItem('smartcart_user')
      if (stored) {
        const user = JSON.parse(stored)
        const token = user?.token || user?.access_token
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
      }

      let sessionId = localStorage.getItem('smartcart_session_id')
      if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substring(2, 15)
        localStorage.setItem('smartcart_session_id', sessionId)
      }
      config.headers['X-Session-ID'] = sessionId
    } catch (err) {
      console.error('Error attaching auth headers:', err)
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default api
export { API_URL }
