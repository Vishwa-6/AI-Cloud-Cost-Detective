import type { ProgressState } from '../hooks/useScanWebSocket';

interface ScanProgressProps {
  progress: ProgressState;
  error: string | null;
}

export default function ScanProgress({ progress, error }: ScanProgressProps) {
  const steps = [
    { key: 'fetching_resources', label: 'Fetching AWS Resources' },
    { key: 'analyzing', label: 'Analyzing with AI' },
    { key: 'saving', label: 'Saving Results' },
    { key: 'complete', label: 'Scan Complete' },
  ];

  return (
    <div className="w-full bg-[#111113] border border-zinc-800 rounded-2xl p-6 shadow-xl mt-6">
      <h3 className="text-lg font-semibold text-zinc-200 mb-6">Scan Progress</h3>
      
      <div className="space-y-4">
        {steps.map((step) => {
          const stepData = progress[step.key as keyof ProgressState];
          const isPending = stepData.status === 'pending';
          const isInProgress = stepData.status === 'in_progress';
          const isDone = stepData.status === 'done';
          const isError = stepData.status === 'error';

          let icon = (
            <div className="w-6 h-6 rounded-full border-2 border-zinc-700 bg-zinc-800 flex-shrink-0" />
          );

          if (isInProgress) {
            icon = (
              <div className="w-6 h-6 rounded-full border-2 border-purple-500 border-t-transparent animate-spin flex-shrink-0" />
            );
          } else if (isDone) {
            icon = (
              <div className="w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
              </div>
            );
          } else if (isError) {
            icon = (
              <div className="w-6 h-6 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12"></path></svg>
              </div>
            );
          }

          return (
            <div key={step.key} className={`flex items-start gap-4 ${isPending ? 'opacity-40' : 'opacity-100'} transition-opacity duration-300`}>
              <div className="mt-0.5">{icon}</div>
              <div>
                <p className={`text-sm font-medium ${isDone ? 'text-zinc-200' : isError ? 'text-red-400' : 'text-zinc-300'}`}>
                  {step.label}
                </p>
                {isError && stepData.message && (
                  <p className="text-xs text-red-400/80 mt-1">{stepData.message}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {error && (
        <div className="mt-6 bg-red-500/10 border border-red-500/30 text-red-400 text-sm p-4 rounded-xl flex items-start">
          <svg className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
