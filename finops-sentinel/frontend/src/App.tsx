import { Routes, Route, useNavigate, Link, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ScanTrigger from './components/ScanTrigger';
import ScanProgress from './components/ScanProgress';
import FindingsDashboard from './components/FindingsDashboard';
import FindingsChart from './components/FindingsChart';
import HistoryPage from './pages/HistoryPage';
import { useScanWebSocket } from './hooks/useScanWebSocket';


function HomePage() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleAuthError = () => {
    logout();
    navigate('/login');
  };

  const {
    progress,
    finalResult,
    isScanning,
    error,
    startScan
  } = useScanWebSocket(token, handleAuthError);
  
  return (
    <div className="min-h-screen bg-[#09090B] text-white flex flex-col items-center p-6">
      <div className="w-full max-w-5xl flex flex-col gap-8 mt-10">
        
        {/* Header Bar */}
        <div className="flex items-center justify-between bg-[#111113] border border-zinc-800 rounded-2xl p-6 shadow-xl hover:border-purple-500/40 transition">
          <div>
            <h1 className="text-3xl font-bold">
              FinOps Sentinel
            </h1>
            <p className="text-sm text-zinc-400 mt-1">AI-Powered AWS Cost Analysis</p>
          </div>
          
          <div className="flex items-center gap-6">
            <nav className="hidden sm:flex gap-4 mr-4">
              <Link to="/" className={`text-sm font-medium transition-colors ${location.pathname === '/' ? 'text-purple-400' : 'text-zinc-400 hover:text-zinc-200'}`}>New Scan</Link>
              <Link to="/history" className={`text-sm font-medium transition-colors ${location.pathname === '/history' ? 'text-purple-400' : 'text-zinc-400 hover:text-zinc-200'}`}>History</Link>
            </nav>
            <div className="text-right hidden sm:block">
              <p className="text-xs text-zinc-400 uppercase tracking-wider font-semibold">Logged in as</p>
              <p className="text-sm font-medium text-zinc-200">{user?.email}</p>
            </div>
            <button 
              onClick={logout}
              className="bg-[#09090B] hover:bg-zinc-800 border border-zinc-700 text-zinc-300 hover:text-white text-sm font-medium py-2 px-5 rounded-lg transition-all"
            >
              Log Out
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        {finalResult && !isScanning ? (
          /* ── Results view: sidebar + full findings ── */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            {/* Left sidebar: chart + new scan button */}
            <div className="col-span-1 flex flex-col gap-5">
              <FindingsChart findings={finalResult.findings ?? []} />
              <ScanTrigger onStart={startScan} isScanning={isScanning} />
            </div>
            {/* Right: full findings dashboard */}
            <div className="col-span-1 lg:col-span-2">
              <FindingsDashboard
                findings={finalResult.findings ?? []}
                summary={finalResult.summary}
              />
            </div>
          </div>
        ) : (
          /* ── Idle / scanning view ── */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Scan Control Panel */}
            <div className="col-span-1">
              <ScanTrigger onStart={startScan} isScanning={isScanning} />
            </div>

            {/* Progress / empty state */}
            <div className="col-span-1 lg:col-span-2">
              {(!isScanning && !error && Object.values(progress).every(s => s.status === 'pending')) ? (
                <div className="bg-[#111113] border border-zinc-800 rounded-2xl p-8 shadow-xl h-full min-h-[400px] flex items-center justify-center hover:border-purple-500/40 transition">
                  <div className="text-center">
                    <svg className="w-16 h-16 text-zinc-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    <h3 className="text-lg font-medium text-zinc-400">No active scans</h3>
                    <p className="text-sm text-zinc-500 mt-2">Select a data source and trigger a scan.</p>
                  </div>
                </div>
              ) : (
                <ScanProgress progress={progress} error={error} />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <>
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#18181b',
            color: '#fff',
            border: '1px solid #27272a',
          },
        }} 
      />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        
        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
