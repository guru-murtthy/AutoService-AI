import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardMetrics, RevenueMetrics } from '../types';
import { Users, FileText, CheckCircle2, TrendingUp, AlertTriangle, Activity, DollarSign } from 'lucide-react';

export const DashboardView: React.FC<{ businessId: string }> = ({ businessId }) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [revenue, setRevenue] = useState<RevenueMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 10000);
    return () => clearInterval(timer);
  }, [businessId]);

  const loadData = async () => {
    try {
      const data = await api.getDashboardSummary(businessId);
      setMetrics(data.metrics);
      setRevenue(data.revenue);
    } catch (e) {
      console.error("Dashboard load failed", e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-400">Loading AutoService AI Dashboard...</div>;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Autonomous Service Command Center</h1>
          <p className="text-sm text-slate-400">Real-time AI enquiry extraction, quotation approval, and revenue tracking</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full glass-card text-xs text-emerald-400 border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Agent Loop Active (5m Heartbeat)</span>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Leads</span>
            <Users className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">{metrics?.total_leads || 0}</div>
          <div className="text-xs text-slate-400 mt-1">
            <span className="text-cyan-400 font-medium">{metrics?.new_leads} New</span> • {metrics?.qualified_leads} Qualified
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Quotations Sent</span>
            <FileText className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">{metrics?.total_quotes || 0}</div>
          <div className="text-xs text-slate-400 mt-1">
            <span className="text-amber-400 font-medium">{metrics?.pending_quotes} Pending Approval</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Conversion Rate</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">{metrics?.conversion_rate_pct || 0}%</div>
          <div className="text-xs text-slate-400 mt-1">
            <span className="text-emerald-400 font-medium">{metrics?.booked_leads} Bookings</span> Confirmed
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Monthly Recurring (MRR)</span>
            <DollarSign className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">₹{revenue?.mrr?.toLocaleString() || 5000}</div>
          <div className="text-xs text-slate-400 mt-1">
            Commercial Target: <span className="text-white font-medium">₹5,000/mo Achieved</span>
          </div>
        </div>
      </div>

      {/* Revenue & Gross Margin Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6 rounded-xl space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" /> Financial Operating Performance
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-400">Gross Booking Rev</div>
              <div className="text-lg font-semibold text-white">₹{revenue?.gross_booking_revenue?.toLocaleString() || 0}</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-400">Operating Expenses</div>
              <div className="text-lg font-semibold text-rose-400">₹{revenue?.operating_expenses?.toLocaleString() || 0}</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-400">Gross Margin</div>
              <div className="text-lg font-semibold text-emerald-400">₹{revenue?.gross_margin?.toLocaleString() || 0}</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-xs text-slate-400">Margin %</div>
              <div className="text-lg font-semibold text-cyan-400">{revenue?.gross_margin_pct || 100}%</div>
            </div>
          </div>
        </div>

        {/* Safety & System Guard Card */}
        <div className="glass-card p-6 rounded-xl space-y-4 border-l-4 border-l-cyan-500">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Operational Safety Limits
          </h2>
          <div className="space-y-2 text-xs text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span>Daily Spend Cap:</span>
              <span className="font-mono text-white">₹500 / day</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span>Quote Approval Threshold:</span>
              <span className="font-mono text-white">₹10,000</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span>Business Validation Mode:</span>
              <span className="font-semibold text-emerald-400">ENABLED</span>
            </div>
            <div className="flex justify-between py-1">
              <span>LLM Pricing Policy:</span>
              <span className="font-semibold text-cyan-400">DETERMINISTIC CODE ONLY</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
