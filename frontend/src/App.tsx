import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, MessageSquare, FileText, BarChart3, ShieldAlert, Cpu, Settings, ExternalLink } from 'lucide-react';
import { DashboardView } from './pages/Dashboard';
import { LeadsView } from './pages/Leads';
import { EnquirySimulatorView } from './pages/EnquirySimulator';
import { QuotationsView } from './pages/Quotations';
import { ReportsView } from './pages/Reports';
import { EmergencyStopView } from './pages/EmergencyStop';
import { CustomerChatView } from './pages/CustomerChat';
import { PricingSettingsView } from './pages/PricingSettings';
import { api } from './services/api';

export const App: React.FC = () => {
  const [businessId, setBusinessId] = useState('demo_business_id');
  const [emergencyActive, setEmergencyActive] = useState(false);
  const location = useLocation();

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const res = await api.getEmergencyStatus();
      setEmergencyActive(res.is_active);
    } catch (e) {}
  };

  // If on customer chat page, render standalone full-screen chat
  if (location.pathname.startsWith('/chat/')) {
    return <CustomerChatView />;
  }

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/leads', label: 'CRM Leads', icon: Users },
    { path: '/enquiries', label: 'AI Enquiry Sandbox', icon: MessageSquare },
    { path: '/quotations', label: 'Quotation Engine', icon: FileText },
    { path: '/reports', label: 'Daily Reports', icon: BarChart3 },
    { path: '/settings', label: 'Pricing Profiles', icon: Settings },
    { path: '/emergency', label: 'Emergency Stop', icon: ShieldAlert },
  ];

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 glass-card border-r border-slate-800 flex flex-col z-20">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl gradient-btn flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-base text-white tracking-tight">AutoService AI</div>
            <div className="text-[10px] text-cyan-400 font-medium tracking-wide">PILOT MODE • REAL DB</div>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                  active
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}

          <div className="pt-4 border-t border-slate-800/80">
            <Link
              to={`/chat/${businessId}`}
              target="_blank"
              className="flex items-center justify-between px-3.5 py-2 rounded-lg text-xs font-semibold text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 hover:bg-emerald-900/40 transition"
            >
              <span>Public Web Chat Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>
        </nav>

        <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-500 space-y-1">
          <div>Target: <span className="text-amber-400 font-semibold">₹5,000 / mo</span></div>
          <div>Mode: <span className="text-cyan-400 font-semibold">PILOT</span></div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Emergency Stop Top Banner */}
        {emergencyActive && (
          <div className="bg-rose-600 text-white px-4 py-2 text-xs font-bold flex items-center justify-between animate-pulse">
            <span className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4" /> EMERGENCY STOP IS CURRENTLY ACTIVE — ALL AUTONOMOUS ACTIONS & MESSAGING HALTED
            </span>
            <Link to="/emergency" className="underline text-white font-mono text-[11px]">Manage Killswitch</Link>
          </div>
        )}

        {/* Top Header Bar */}
        <header className="h-14 border-b border-slate-800 glass-card px-6 flex items-center justify-between z-10">
          <div className="text-xs text-slate-400 font-medium">
            Business: <span className="text-white font-bold">Indian Travel & Tour Agency #01</span>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="px-2.5 py-1 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-300 font-mono text-[11px]">
              APP_MODE: pilot
            </span>
          </div>
        </header>

        {/* Dynamic Route View */}
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<DashboardView businessId={businessId} />} />
            <Route path="/leads" element={<LeadsView businessId={businessId} />} />
            <Route path="/enquiries" element={<EnquirySimulatorView businessId={businessId} />} />
            <Route path="/quotations" element={<QuotationsView businessId={businessId} />} />
            <Route path="/reports" element={<ReportsView businessId={businessId} />} />
            <Route path="/settings" element={<PricingSettingsView businessId={businessId} />} />
            <Route path="/emergency" element={<EmergencyStopView />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default App;
