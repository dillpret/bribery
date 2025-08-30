import notificationService from '@/services/notification'

describe('Notification Service', () => {
  let mockManager
  
  beforeEach(() => {
    // Create a mock notification manager
    mockManager = {
      addNotification: jest.fn().mockReturnValue(1),
      removeNotification: jest.fn(),
      clearAllNotifications: jest.fn()
    }
    
    // Reset the notification manager
    notificationService.setNotificationManager(mockManager)
    
    // Spy on console.warn
    jest.spyOn(console, 'warn').mockImplementation(() => {})
  })
  
  afterEach(() => {
    jest.restoreAllMocks()
  })
  
  it('shows success notification', () => {
    const message = 'Test success message'
    const options = { title: 'Success' }
    
    const result = notificationService.success(message, options)
    
    expect(result).toBe(1)
    expect(mockManager.addNotification).toHaveBeenCalledWith({
      type: 'success',
      message,
      title: 'Success'
    })
  })
  
  it('shows error notification', () => {
    const message = 'Test error message'
    const options = { title: 'Error' }
    
    const result = notificationService.error(message, options)
    
    expect(result).toBe(1)
    expect(mockManager.addNotification).toHaveBeenCalledWith({
      type: 'error',
      message,
      title: 'Error'
    })
  })
  
  it('shows warning notification', () => {
    const message = 'Test warning message'
    const options = { title: 'Warning' }
    
    const result = notificationService.warning(message, options)
    
    expect(result).toBe(1)
    expect(mockManager.addNotification).toHaveBeenCalledWith({
      type: 'warning',
      message,
      title: 'Warning'
    })
  })
  
  it('shows info notification', () => {
    const message = 'Test info message'
    const options = { title: 'Info' }
    
    const result = notificationService.info(message, options)
    
    expect(result).toBe(1)
    expect(mockManager.addNotification).toHaveBeenCalledWith({
      type: 'info',
      message,
      title: 'Info'
    })
  })
  
  it('removes notification by id', () => {
    const id = 123
    
    notificationService.remove(id)
    
    expect(mockManager.removeNotification).toHaveBeenCalledWith(id)
  })
  
  it('clears all notifications', () => {
    notificationService.clearAll()
    
    expect(mockManager.clearAllNotifications).toHaveBeenCalled()
  })
  
  it('warns when notification manager is not set', () => {
    // Create a spy on console.warn
    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    
    // Reset the notification manager by creating a new Vue instance
    // without actually passing a real component
    notificationService.setNotificationManager(undefined);
    
    const result = notificationService.info('Test message')
    
    expect(consoleWarnSpy).toHaveBeenCalled()
    expect(result).toBe(false)
    
    // Restore console.warn
    consoleWarnSpy.mockRestore()
  })
})
