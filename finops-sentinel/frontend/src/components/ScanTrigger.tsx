import { useState } from 'react';

interface ScanTriggerProps {
  onStart: (mode: string) => void;
  isScanning: boolean;
}

export default function ScanTrigger({ onStart, isScanning }: ScanTriggerProps) {
  const [mode, setMode] = useState('mock');

  return (
    <div className="bg-[#111113] border border-zinc-800 rounded-2xl p-8 shadow-xl flex flex-col items-center justify-center min-h-[400px] text-center hover:border-purple-500/40 transition">
      <div className="w-16 h-16 bg-purple-500/20 text-purple-400 rounded-full flex items-center justify-center mb-6">
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
      </div>
      
      <h3 className="text-xl font-semibold text-zinc-200 mb-2">Run a Cost Scan</h3>
      <p className="text-sm text-zinc-400 mb-6 leading-relaxed">
        Trigger a full AI analysis of your AWS footprint to discover right-sizing opportunities and idle resources.
      </p>

      <div className="w-full space-y-4">
        <div className="text-left">
          <label className="block text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
            Data Source
          </label>
          <select 
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            disabled={isScanning}
            className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-4 py-3 text-zinc-200 focus:outline-none focus:border-purple-500 transition-colors disabled:opacity-50 appearance-none"
          >
            <option value="mock">Mock Data (Fast Testing)</option>
            <option value="live">Live AWS (Requires Config)</option>
          </select>
        </div>

        <button 
          onClick={() => onStart(mode)}
          disabled={isScanning}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-xl transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/25 mt-4"
        >
          {isScanning ? 'Scan in Progress...' : 'Start Scan'}
        </button>
      </div>
    </div>
  );
}
