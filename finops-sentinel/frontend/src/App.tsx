import { useState } from 'react'

function App() {
  const [backendStatus, setBackendStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const checkBackend = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/health')
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      const data = await res.json()
      setBackendStatus(JSON.stringify(data, null, 2))
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend')
      setBackendStatus(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4 font-sans">
      <div className="max-w-md w-full bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700">
        <h1 className="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
          FinOps Sentinel
        </h1>
        <p className="text-gray-400 text-center mb-8">AI-powered AWS cost analysis tool</p>
        
        <div className="flex flex-col items-center">
          <button 
            onClick={checkBackend}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg transition-all duration-200 shadow-[0_0_15px_rgba(37,99,235,0.5)] hover:shadow-[0_0_25px_rgba(59,130,246,0.6)] active:scale-95"
          >
            Check Backend Connection
          </button>
          
          <div className="w-full mt-6 min-h-[100px]">
            {backendStatus && (
              <div className="bg-gray-950 rounded-lg p-4 font-mono text-sm border border-emerald-900 shadow-inner">
                <span className="text-emerald-400 block mb-2 text-xs uppercase tracking-wider">Response:</span>
                <pre className="text-gray-300 overflow-x-auto">{backendStatus}</pre>
              </div>
            )}
            
            {error && (
              <div className="bg-red-950/50 rounded-lg p-4 font-mono text-sm border border-red-900 shadow-inner text-red-400">
                <span className="block mb-2 text-xs uppercase tracking-wider">Error:</span>
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
