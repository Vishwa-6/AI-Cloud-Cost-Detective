import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import FindingsDashboard from '../components/FindingsDashboard';
import FindingsChart from '../components/FindingsChart';
import toast from 'react-hot-toast';

interface ScanSummary {
  id: number;
  mode: string;
  total_resources_scanned: number;
  total_issues_found: number;
  total_estimated_monthly_savings_usd: number;
  created_at: string;
}

export default function HistoryPage() {
  const { token } = useAuth();
  const [scans, setScans] = useState<ScanSummary[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  
  const [selectedScanId, setSelectedScanId] = useState<number | null>(null);
  const [detailedScan, setDetailedScan] = useState<any | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    if (!token) return;
    
    apiClient.get('/api/scans')
    .then(res => {
      setScans(res.data);
    })
    .catch(err => {
      console.error(err);
      toast.error('Failed to load scan history.');
    })
    .finally(() => {
      setLoadingList(false);
    });
  }, [token]);

  const loadScanDetails = (id: number) => {
    setSelectedScanId(id);
    setLoadingDetail(true);
    
    apiClient.get(`/api/scans/${id}`)
    .then(res => {
      setDetailedScan(res.data);
    })
    .catch(err => {
      console.error(err);
      toast.error('Failed to load scan details.');
      setSelectedScanId(null);
    })
    .finally(() => {
      setLoadingDetail(false);
    });
  };

  const handleBackToList = () => {
    setSelectedScanId(null);
    setDetailedScan(null);
  };

  return (
    <div className="min-h-screen bg-[#09090B] text-white flex flex-col items-center p-6">
      <div className="w-full max-w-5xl flex flex-col gap-8 mt-10">
        
        {/* Header Bar */}
        <div className="flex items-center justify-between bg-[#111113] border border-zinc-800 rounded-2xl p-6 shadow-xl hover:border-purple-500/40 transition">
          <div>
            <h1 className="text-3xl font-bold">Scan History</h1>
            <p className="text-sm text-zinc-400 mt-1">Review your past AWS cost analyses</p>
          </div>
          <div className="flex gap-4">
            {selectedScanId && (
              <button 
                onClick={handleBackToList}
                className="bg-zinc-800 hover:bg-zinc-700 text-sm font-medium py-2 px-4 rounded-lg transition-all"
              >
                ← Back to List
              </button>
            )}
            <Link 
              to="/"
              className="bg-zinc-800 hover:bg-zinc-700 text-sm font-medium py-2 px-4 rounded-lg transition-all"
            >
              Return to Run Scan Page
            </Link>
          </div>
        </div>

        {/* Detailed View */}
        {selectedScanId && detailedScan && !loadingDetail && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start animate-fadeIn">
            <div className="col-span-1 flex flex-col gap-5">
              <FindingsChart findings={detailedScan.findings ?? []} />
            </div>
            <div className="col-span-1 lg:col-span-2">
              <FindingsDashboard 
                findings={detailedScan.findings ?? []} 
                summary={detailedScan.summary} 
              />
            </div>
          </div>
        )}

        {/* Detail Loading Skeleton */}
        {selectedScanId && loadingDetail && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-pulse flex flex-col items-center">
              <div className="h-12 w-12 bg-purple-500/20 rounded-full mb-4"></div>
              <div className="h-4 w-32 bg-zinc-800 rounded"></div>
            </div>
          </div>
        )}

        {/* List View */}
        {!selectedScanId && (
          <div className="bg-[#111113] border border-zinc-800 rounded-2xl shadow-xl overflow-hidden">
            {loadingList ? (
              <div className="p-8 flex flex-col gap-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="animate-pulse flex items-center justify-between p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
                    <div className="flex flex-col gap-2">
                      <div className="h-4 w-48 bg-zinc-800 rounded"></div>
                      <div className="h-3 w-24 bg-zinc-800 rounded"></div>
                    </div>
                    <div className="h-6 w-20 bg-zinc-800 rounded"></div>
                  </div>
                ))}
              </div>
            ) : scans.length === 0 ? (
              <div className="p-12 text-center">
                <h3 className="text-lg font-medium text-zinc-400">No scans found</h3>
                <p className="text-sm text-zinc-500 mt-2">Go to the dashboard to run your first scan.</p>
              </div>
            ) : (
              <div className="divide-y divide-zinc-800/50">
                {scans.map(scan => (
                  <div 
                    key={scan.id} 
                    onClick={() => loadScanDetails(scan.id)}
                    className="flex items-center justify-between p-5 hover:bg-zinc-800/30 cursor-pointer transition-colors group"
                  >
                    <div>
                      <p className="text-sm font-medium text-zinc-200 group-hover:text-purple-400 transition-colors">
                        Scan #{scan.id} • {new Date(scan.created_at).toLocaleString()}
                      </p>
                      <p className="text-xs text-zinc-500 mt-1">
                        Mode: {scan.mode.toUpperCase()} • {scan.total_resources_scanned} resources scanned
                      </p>
                    </div>
                    <div className="text-right flex items-center gap-4">
                      <div>
                        <p className="text-sm font-bold text-green-400">${scan.total_estimated_monthly_savings_usd.toFixed(2)}/mo</p>
                        <p className="text-xs text-zinc-500">{scan.total_issues_found} issues</p>
                      </div>
                      <svg className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path></svg>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
