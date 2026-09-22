import React, { useState } from 'react';
import { api } from '../services/api';
import { Calculator, FileText, CheckCircle, ShieldAlert } from 'lucide-react';

export const QuotationsView: React.FC<{ businessId: string }> = ({ businessId }) => {
  const [vehicleType, setVehicleType] = useState('7-seater');
  const [durationDays, setDurationDays] = useState(3);
  const [estimatedKm, setEstimatedKm] = useState(850);
  const [calcResult, setCalcResult] = useState<any>(null);

  const handleCalculate = async () => {
    try {
      const res = await api.calculateQuote(businessId, vehicleType, durationDays, estimatedKm);
      setCalcResult(res);
    } catch (e) {
      alert("Error running calculation");
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Calculator className="w-6 h-6 text-cyan-400" /> Deterministic Quotation Engine & PDF Generator
        </h1>
        <p className="text-sm text-slate-400">Deterministic pricing math derived strictly from business rates (LLM never invents prices)</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Interactive Price Calculator */}
        <div className="glass-card p-6 rounded-xl space-y-4">
          <h2 className="text-md font-semibold text-white border-b border-slate-800 pb-2">Deterministic Price Calculator</h2>
          
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Vehicle Category</label>
            <select
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
            >
              <option value="5-seater">5-Seater Sedan (Base ₹1,999/day)</option>
              <option value="7-seater">7-Seater SUV Ertiga/Innova (Base ₹2,599/day)</option>
              <option value="tempo-traveller">Tempo Traveller 12-Seater (Base ₹4,500/day)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Trip Duration (Days)</label>
              <input
                type="number"
                min="1"
                value={durationDays}
                onChange={(e) => setDurationDays(parseInt(e.target.value) || 1)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Estimated Distance (KM)</label>
              <input
                type="number"
                min="0"
                value={estimatedKm}
                onChange={(e) => setEstimatedKm(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            onClick={handleCalculate}
            className="w-full py-2.5 rounded-lg gradient-btn text-white font-semibold text-sm flex items-center justify-center gap-2"
          >
            <Calculator className="w-4 h-4" /> Calculate Deterministic Price Breakdown
          </button>
        </div>

        {/* Calculation Result Breakdown */}
        <div className="glass-card p-6 rounded-xl space-y-4 border-l-4 border-l-cyan-500">
          <h2 className="text-md font-semibold text-white border-b border-slate-800 pb-2">Calculation Breakdown</h2>
          
          {calcResult ? (
            <div className="space-y-4 text-xs">
              <div className="space-y-2">
                {calcResult.items.map((item: any, idx: number) => (
                  <div key={idx} className="flex justify-between py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-300">{item.description}</span>
                    <span className="font-mono text-white">₹{item.total.toLocaleString()}</span>
                  </div>
                ))}
              </div>

              <div className="bg-slate-900/80 p-3 rounded-lg space-y-1 text-xs pt-2">
                <div className="flex justify-between text-slate-400">
                  <span>Subtotal:</span>
                  <span className="font-mono text-white">₹{calcResult.subtotal.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>GST Tax (5%):</span>
                  <span className="font-mono text-white">₹{calcResult.tax.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-base font-bold text-emerald-400 pt-2 border-t border-slate-800">
                  <span>Grand Total:</span>
                  <span className="font-mono">₹{calcResult.total.toLocaleString()}</span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Quotation requires Human Owner Approval before being sent to customer.</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-xs">
              Click Calculate above to view exact line-item rates, driver allowance, and GST tax calculations.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
