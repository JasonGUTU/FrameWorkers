// Long polling service for real-time updates

class PollingService {
  constructor() {
    this.pollingIntervals = new Map()
    this.callbacks = new Map()
  }

  startPolling(key, fetchFn, interval = 2000, callback = null) {
    // Stop existing polling if any
    this.stopPolling(key)

    // Store callback
    if (callback) {
      this.callbacks.set(key, callback)
    }

    // Initial fetch
    fetchFn()
      .then(response => {
        if (callback) {
          callback(response.data)
        }
      })
      .catch(error => {
        console.error(`Polling error for ${key}:`, error)
      })

    // Set up interval
    const intervalId = setInterval(() => {
      fetchFn()
        .then(response => {
          if (callback) {
            callback(response.data)
          }
        })
        .catch(error => {
          console.error(`Polling error for ${key}:`, error)
        })
    }, interval)

    this.pollingIntervals.set(key, intervalId)
  }

  stopPolling(key) {
    const intervalId = this.pollingIntervals.get(key)
    if (intervalId) {
      clearInterval(intervalId)
      this.pollingIntervals.delete(key)
    }
    this.callbacks.delete(key)
  }

  stopAll() {
    this.pollingIntervals.forEach((intervalId) => {
      clearInterval(intervalId)
    })
    this.pollingIntervals.clear()
    this.callbacks.clear()
  }
}

export default new PollingService()
