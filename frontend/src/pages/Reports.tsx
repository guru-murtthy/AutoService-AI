import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DailyReport } from '../types';
import { BarChart3, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';

export const ReportsView: React.FC<{ businessId: string }> = ({ businessId }) => {
  const [report, setReport] = useState<DailyReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReport();
  }, [businessId]);

  const loadReport = async () => {
    try {
      const data = await api.getDailyReport(businessId);
      setReport(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-400">Generating Daily Business Report...</div>;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-cyan-400" /> Daily Business Performance Report
          </h1>
          <p className="text-sm text-slate-400">Automated daily summary of enquiries, quotes, bookings, and net contribution</p>
        </div>
        <div className="px-3 py-1 bg-slate-800 text-slate-300 text-xs font-mono rounded-lg border border-slate-700">
          Date: {report?.date || new Date().toISOString().split('T')[0]}
        </div>
      </div>

      <div className="glass-card p-6 rounded-xl space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Total Enquiries</div>
            <div className="text-2xl font-bold text-white mt-1">{report?.enquiries_count || 0}</div>
          </div>
          <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Qualified Leads</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{report?.qualified_leads || 0}</div>
          </div>
          <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Quotes Generated</div>
            <div className="text-2xl font-bold text-blue-400 mt-1">{report?.quotes_generated || 0}</div>
          </div>
          <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Bookings Confirmed</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{report?.bookings_count || 0}</div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-3">
          <h3 className="text-sm font-semibold text-white">Daily Financial Breakdown (Estimated vs Net)</h3>
          
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-300">Gross Revenue Collected:</span>
              <span className="font-mono text-emerald-400 font-bold">₹{report?.revenue_amount?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-300">Estimated AI API Costs:</span>
              <span className="font-mono text-rose-400 font-bold">- ₹{report?.estimated_ai_cost?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between py-2 text-sm font-bold pt-2">
              <span className="text-white">Net Business Contribution:</span>
              <span className="font-mono text-cyan-400">₹{report?.net_contribution?.toLocaleString() || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
