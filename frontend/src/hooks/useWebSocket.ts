import { useEffect, useRef, useCallback } from 'react'

interface UseWebSocketOptions {
  onMessage?: (data: unknown) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number>()

  const connect = useCallback(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      wsRef.current = ws
      ws.send(JSON.stringify({ type: 'subscribe', channel: 'all' }))
      options.onConnect?.()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        options.onMessage?.(data)
      } catch {
        // ignore non-json messages
      }
    }

    ws.onclose = () => {
      wsRef.current = null
      options.onDisconnect?.()
      reconnectTimeoutRef.current = window.setTimeout(connect, 5000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [options])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { isConnected: !!wsRef.current }
}
