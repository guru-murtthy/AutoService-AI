import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ShieldAlert, Octagon, CheckCircle, AlertTriangle } from 'lucide-react';

export const EmergencyStopView: React.FC = () => {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [reason, setReason] = useState("Manual administrative killswitch triggered");

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const data = await api.getEmergencyStatus();
      setStatus(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleHalt = async () => {
    setLoading(true);
    try {
      const res = await api.triggerEmergencyStop(reason);
      setStatus(res);
      alert("EMERGENCY STOP ACTIVATED! All outbound tasks and spending halted.");
    } catch (e) {
      alert("Failed to activate emergency stop");
    } finally {
      setLoading(false);
    }
  };

  const handleResume = async () => {
    setLoading(true);
    try {
      const res = await api.resumeNormalOperations();
      setStatus(res);
      alert("Operations resumed successfully.");
    } catch (e) {
      alert("Failed to resume operations");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-rose-500" /> Emergency Killswitch Controls
        </h1>
        <p className="text-sm text-slate-400">Instantly halt outbound messaging, payments, and agent tasks while preserving audit logs</p>
      </div>

      <div className={`glass-card p-6 rounded-xl border-2 ${status?.is_active ? 'border-rose-600 bg-rose-950/20' : 'border-emerald-600/50'}`}>
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <Octagon className={`w-8 h-8 ${status?.is_active ? 'text-rose-500 animate-pulse' : 'text-emerald-400'}`} />
            <div>
              <div className="text-sm font-semibold text-slate-300">System Autonomous Status</div>
              <div className={`text-xl font-black tracking-wide ${status?.is_active ? 'text-rose-400' : 'text-emerald-400'}`}>
                {status?.is_active ? "HALTED (EMERGENCY STOP ACTIVE)" : "OPERATIONAL (NORMAL MODE)"}
              </div>
            </div>
          </div>
        </div>

        {status?.is_active ? (
          <div className="py-6 space-y-4">
            <div className="p-4 bg-rose-950/60 border border-rose-800 text-xs text-rose-200 rounded-lg space-y-1">
              <div><strong>Activated By:</strong> {status.activated_by || "Admin"}</div>
              <div><strong>Timestamp:</strong> {status.activated_at ? new Date(status.activated_at).toLocaleString() : "N/A"}</div>
              <div><strong>Reason:</strong> {status.reason}</div>
            </div>
            <button
              onClick={handleResume}
              disabled={loading}
              className="w-full py-3 rounded-lg gradient-btn text-white font-bold text-sm"
            >
              Resume Normal Operations
            </button>
          </div>
        ) : (
          <div className="py-6 space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Reason for Emergency Stop</label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
              />
            </div>
            <button
              onClick={handleHalt}
              disabled={loading}
              className="w-full py-3 rounded-lg emergency-btn text-white font-bold text-sm flex items-center justify-center gap-2"
            >
              <ShieldAlert className="w-5 h-5" /> ACTIVATE EMERGENCY STOP NOW
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
