import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Settings, Car, Save, ShieldCheck, Check } from 'lucide-react';

export const PricingSettingsView: React.FC<{ businessId: string }> = ({ businessId }) => {
  const [configs, setConfigs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadPricing();
  }, [businessId]);

  const loadPricing = async () => {
    try {
      const res = await axios.get(`/api/v1/pricing/${businessId}`);
      setConfigs(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (cfg: any) => {
    try {
      await axios.post(`/api/v1/pricing/${businessId}`, cfg);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      loadPricing();
    } catch (e) {
      alert("Failed to update pricing profile");
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-400">Loading Pricing Profiles...</div>;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Settings className="w-6 h-6 text-cyan-400" /> Business Pricing Profiles & Terms
          </h1>
          <p className="text-sm text-slate-400">Configure vehicle rates, driver allowances, cancellation terms, and included kilometres</p>
        </div>
        {saved && (
          <span className="px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-semibold flex items-center gap-1">
            <Check className="w-4 h-4" /> Pricing Profile Saved!
          </span>
        )}
      </div>

      <div className="space-y-6">
        {configs.map((cfg) => (
          <div key={cfg.vehicle_type} className="glass-card p-6 rounded-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Car className="w-5 h-5 text-cyan-400" />
                <h2 className="text-md font-bold text-white capitalize">{cfg.vehicle_type} Profile</h2>
              </div>
              <button
                onClick={() => handleSave(cfg)}
                className="px-4 py-1.5 rounded-lg gradient-btn text-white font-semibold text-xs flex items-center gap-1.5 shadow"
              >
                <Save className="w-3.5 h-3.5" /> Save Changes
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Base Price / Day (₹)</label>
                <input
                  type="number"
                  value={cfg.base_price_per_day}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 0;
                    setConfigs(configs.map(c => c.vehicle_type === cfg.vehicle_type ? { ...c, base_price_per_day: val } : c));
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Rate / Extra KM (₹)</label>
                <input
                  type="number"
                  value={cfg.rate_per_km}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 0;
                    setConfigs(configs.map(c => c.vehicle_type === cfg.vehicle_type ? { ...c, rate_per_km: val } : c));
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Driver Allowance / Day (₹)</label>
                <input
                  type="number"
                  value={cfg.driver_allowance_per_day}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 0;
                    setConfigs(configs.map(c => c.vehicle_type === cfg.vehicle_type ? { ...c, driver_allowance_per_day: val } : c));
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
              <div>
                <label className="block text-slate-400 mb-1">Cancellation Policy</label>
                <textarea
                  rows={2}
                  value={cfg.cancellation_policy || ''}
                  onChange={(e) => {
                    const val = e.target.value;
                    setConfigs(configs.map(c => c.vehicle_type === cfg.vehicle_type ? { ...c, cancellation_policy: val } : c));
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Terms & Conditions</label>
                <textarea
                  rows={2}
                  value={cfg.terms_and_conditions || ''}
                  onChange={(e) => {
                    const val = e.target.value;
                    setConfigs(configs.map(c => c.vehicle_type === cfg.vehicle_type ? { ...c, terms_and_conditions: val } : c));
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
