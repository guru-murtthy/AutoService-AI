import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { LeadItem } from '../types';
import { MapPin, Calendar, Car, Shield, UserCheck } from 'lucide-react';

const STAGES = ["NEW", "QUALIFIED", "QUOTED", "FOLLOW_UP", "BOOKED", "LOST"];

export const LeadsView: React.FC<{ businessId: string }> = ({ businessId }) => {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
  }, [businessId]);

  const loadLeads = async () => {
    try {
      const data = await api.getLeads(businessId);
      setLeads(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (leadId: string, newStatus: string) => {
    try {
      await api.updateLeadStatus(leadId, newStatus);
      loadLeads();
    } catch (e) {
      alert("Failed to update lead status");
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-400">Loading Leads CRM...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Lead Pipeline & Engagement Scoring</h1>
          <p className="text-sm text-slate-400">Manage customer travel enquiries and pipeline stages</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {STAGES.map((stage) => {
          const stageLeads = leads.filter((l) => l.status === stage);
          return (
            <div key={stage} className="glass-card p-3 rounded-xl min-h-[400px] flex flex-col">
              <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">{stage}</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">{stageLeads.length}</span>
              </div>

              <div className="space-y-3 flex-1 overflow-y-auto">
                {stageLeads.map((lead) => (
                  <div key={lead.id} className="bg-slate-900/90 p-3 rounded-lg border border-slate-800 hover:border-slate-700 transition">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-xs text-white truncate max-w-[110px]">{lead.customer_name}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                        lead.lead_score >= 80 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                        lead.lead_score >= 50 ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        Score: {lead.lead_score}
                      </span>
                    </div>

                    <div className="space-y-1 text-[11px] text-slate-400 mt-2">
                      {lead.destination && (
                        <div className="flex items-center gap-1 text-slate-300">
                          <MapPin className="w-3 h-3 text-cyan-400 shrink-0" />
                          <span className="truncate">{lead.origin || 'Bangalore'} → {lead.destination}</span>
                        </div>
                      )}
                      {lead.vehicle_type && (
                        <div className="flex items-center gap-1">
                          <Car className="w-3 h-3 text-slate-500 shrink-0" />
                          <span>{lead.vehicle_type}</span>
                        </div>
                      )}
                      {lead.travel_date && (
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-slate-500 shrink-0" />
                          <span>{lead.travel_date}</span>
                        </div>
                      )}
                    </div>

                    {/* Quick Move Selector */}
                    <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between">
                      <select
                        value={lead.status}
                        onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                        className="bg-slate-950 text-[10px] text-slate-300 px-1.5 py-1 rounded border border-slate-800 focus:outline-none"
                      >
                        {STAGES.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
