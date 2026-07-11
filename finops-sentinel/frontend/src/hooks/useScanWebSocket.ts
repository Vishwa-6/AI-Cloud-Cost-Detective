import { useState, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';

export type StepStatus = 'pending' | 'in_progress' | 'done' | 'error';
export type ScanStep = 'fetching_resources' | 'analyzing' | 'saving' | 'complete' | 'auth';

export interface ProgressState {
  fetching_resources: { status: StepStatus; message?: string };
  analyzing: { status: StepStatus; message?: string };
  saving: { status: StepStatus; message?: string };
  complete: { status: StepStatus; message?: string };
}

const initialProgress: ProgressState = {
  fetching_resources: { status: 'pending' },
  analyzing: { status: 'pending' },
  saving: { status: 'pending' },
  complete: { status: 'pending' },
};

export function useScanWebSocket(token: string | null, onAuthError: () => void) {
  const [progress, setProgress] = useState<ProgressState>(initialProgress);
  const [finalResult, setFinalResult] = useState<any | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const startScan = useCallback((mode: string) => {
    if (!token) {
      const msg = "You must be logged in to start a scan.";
      setError(msg);
      toast.error(msg);
      onAuthError();
      return;
    }

    // Reset state
    setProgress(initialProgress);
    setFinalResult(null);
    setError(null);
    setIsScanning(true);

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.VITE_WS_HOST || 'localhost:8000';
    const wsUrl = `${wsProtocol}//${wsHost}/api/scan/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send initial auth + mode payload
      ws.send(JSON.stringify({ token, mode }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { step, status, message, result, analysis_id } = data;

        if (step === 'auth' && status === 'error') {
          const msg = message || 'Authentication failed';
          setError(msg);
          toast.error(msg);
          ws.close();
          onAuthError();
          return;
        }

        if (step && status) {
          if (['fetching_resources', 'analyzing', 'saving', 'complete'].includes(step)) {
            setProgress(prev => ({
              ...prev,
              [step]: { status, message }
            }));
          }

          if (step === 'complete' && status === 'success') {
            setFinalResult({ ...result, analysis_id });
            setIsScanning(false);
            toast.success('Scan completed successfully!');
            ws.close();
          } else if (status === 'error') {
            const msg = message || `Error during step: ${step}`;
            setError(msg);
            toast.error(msg);
            setIsScanning(false);
            ws.close();
          }
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onerror = (e) => {
      console.error("WebSocket error:", e);
      const msg = "Failed to connect to the server. Is the backend running?";
      setError(msg);
      toast.error(msg);
      setIsScanning(false);
    };

    ws.onclose = () => {
      if (isScanning && !finalResult && !error) {
         // Connection dropped unexpectedly
         const msg = "Connection lost unexpectedly.";
         setError(msg);
         toast.error(msg);
         setIsScanning(false);
      }
    };

  }, [token, onAuthError, isScanning, finalResult, error]);

  const resetScan = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setProgress(initialProgress);
    setFinalResult(null);
    setError(null);
    setIsScanning(false);
  }, []);

  // Cleanup on unmount
  useCallback(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    progress,
    finalResult,
    isScanning,
    error,
    startScan,
    resetScan
  };
}
