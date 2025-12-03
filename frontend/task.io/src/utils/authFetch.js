import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const authStore = useAuthStore()

export const showReLoginDialog = () => {
  window.dispatchEvent(new CustomEvent('need-login'))
}

export async function authFetch(input, init = {}) {
  const base = 'http://localhost:8000'
  let meRes = await fetch(`${base}/api/v1/auth/me`, {
    headers: {
      'Authorization': `Bearer ${authStore.access_token}`,
      'Accept': 'application/json'
    },
    credentials: 'include'
  })
  if (meRes.status === 401) {
    const refreshRes = await fetch(`${base}/api/v1/auth/refresh`, {
      method: 'POST',
      credentials: 'include'
    })
    if (!refreshRes.ok) {
      authStore.setTokens(null, null)
      authStore.setUserInfo(null, null, null, null, null)
      showReLoginDialog()
      throw new Error('Refresh token expired')
    }
    const { access_token } = await refreshRes.json()
    authStore.setTokens(access_token, authStore.refresh_token)
    meRes = await fetch(`${base}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${authStore.access_token}`,
        'Accept': 'application/json'
      },
      credentials: 'include'
    })
    if (!meRes.ok) {
      showReLoginDialog()
      throw new Error('Failed to re-authenticate')
    }
  }
  const headers = init.headers || {}
  headers['Authorization'] = `Bearer ${authStore.access_token}`
  headers['Accept'] = headers['Accept'] || 'application/json'

  const res = await fetch(base + input, {
    ...init,
    headers,
    credentials: 'include'
  })
  return res
}
