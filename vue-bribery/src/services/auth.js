class AuthService {
  getStorageKey(gameId) {
    return `bribery_game_${gameId}`
  }

  saveAuthState(gameId, authData) {
    if (!gameId) return false

    const storageKey = this.getStorageKey(gameId)
    try {
      const dataToStore = JSON.stringify({
        playerId: authData.playerId,
        username: authData.username,
        isHost: authData.isHost,
        timestamp: Date.now()
      })
      
      localStorage.setItem(storageKey, dataToStore)
      return true
    } catch (error) {
      console.warn('Failed to save auth state:', error)
      return false
    }
  }

  loadAuthState(gameId) {
    if (!gameId) return null
    
    const storageKey = this.getStorageKey(gameId)
    try {
      const storedData = localStorage.getItem(storageKey)
      
      if (!storedData) return null
      
      const parsedData = JSON.parse(storedData)
      return {
        playerId: parsedData.playerId || null,
        username: parsedData.username || null,
        isHost: !!parsedData.isHost
      }
    } catch (error) {
      console.error('Error loading auth state:', error)
      return null
    }
  }

  clearAuthState(gameId) {
    if (!gameId) return
    
    const storageKey = this.getStorageKey(gameId)
    localStorage.removeItem(storageKey)
  }
}

export default new AuthService()
