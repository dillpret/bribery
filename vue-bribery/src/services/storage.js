class StorageService {
  setItem(key, value) {
    try {
      const serializedValue = JSON.stringify(value)
      localStorage.setItem(key, serializedValue)
      return true
    } catch (error) {
      console.error('Error storing data:', error)
      return false
    }
  }

  getItem(key) {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : null
    } catch (error) {
      console.error('Error retrieving data:', error)
      return null
    }
  }

  removeItem(key) {
    try {
      localStorage.removeItem(key)
      return true
    } catch (error) {
      console.error('Error removing data:', error)
      return false
    }
  }

  clear() {
    try {
      localStorage.clear()
      return true
    } catch (error) {
      console.error('Error clearing storage:', error)
      return false
    }
  }
}

export default new StorageService()
