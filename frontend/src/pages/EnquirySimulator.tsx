import React, { useState } from 'react';
import { api } from '../services/api';
import { EnquiryResponse } from '../types';
import { Send, Bot, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';

export const EnquirySimulatorView: React.FC<{ businessId: string }> = ({ businessId }) => {
  const [customerName, setCustomerName] = useState('Rahul Sharma');
  const [phone, setPhone] = useState('+91 98765 43210');
  const [message, setMessage] = useState('I need a 7 seater from Bangalore to Coorg for 3 days starting Oct 10th for 6 people');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EnquiryResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    try {
      const res = await api.submitEnquiry(businessId, customerName, message, phone);
      setResult(res);
    } catch (e) {
      alert("Error submitting enquiry");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-cyan-400" /> Customer Enquiry & AI Requirement Engine
        </h1>
        <p className="text-sm text-slate-400">Test real natural language messages and observe structured extraction & missing info detection</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Input Form */}
        <form onSubmit={handleSubmit} className="glass-card p-6 rounded-xl space-y-4">
          <h2 className="text-md font-semibold text-white border-b border-slate-800 pb-2">Customer Intake Sandbox</h2>
          
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Customer Name</label>
            <input
              type="text"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Phone Number</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Natural Language Enquiry Message</label>
            <textarea
              rows={4}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="e.g. Need a car from Bangalore to Mysore for 2 days next weekend"
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg gradient-btn text-white font-semibold text-sm flex items-center justify-center gap-2"
          >
            <Send className="w-4 h-4" /> {loading ? "Processing AI Extraction..." : "Submit Natural Language Enquiry"}
          </button>
        </form>

        {/* Extraction Result Visualizer */}
        <div className="glass-card p-6 rounded-xl space-y-4 border-l-4 border-l-cyan-500">
          <h2 className="text-md font-semibold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
            <Bot className="w-5 h-5 text-cyan-400" /> Extracted Requirements & Memory Output
          </h2>

          {result ? (
            <div className="space-y-4 text-xs">
              <div className="bg-slate-900 p-3 rounded-lg space-y-1.5 font-mono">
                <div className="text-slate-400 uppercase text-[10px] tracking-wider mb-1 font-sans">Structured JSON Extraction</div>
                <div className="text-cyan-300">origin: <span className="text-white">"{result.extracted.origin}"</span></div>
                <div className="text-cyan-300">destination: <span className="text-white">"{result.extracted.destination}"</span></div>
                <div className="text-cyan-300">vehicle_type: <span className="text-white">"{result.extracted.vehicle_type}"</span></div>
                <div className="text-cyan-300">duration_days: <span className="text-white">{result.extracted.duration_days}</span></div>
                <div className="text-cyan-300">travel_date: <span className="text-white">"{result.extracted.travel_date}"</span></div>
                <div className="text-cyan-300">passenger_count: <span className="text-white">{result.extracted.passenger_count}</span></div>
                <div className="text-cyan-300">confidence: <span className="text-emerald-400">{result.extracted.confidence}</span></div>
              </div>

              {/* Missing Fields Indicator */}
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                  {result.missing_fields.length === 0 ? (
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                  )}
                  Missing Information Check
                </div>
                {result.missing_fields.length === 0 ? (
                  <span className="text-emerald-400">All required travel fields complete! Ready for deterministic quote.</span>
                ) : (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {result.missing_fields.map((f) => (
                      <span key={f} className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800 font-mono text-[10px]">
                        {f}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Automated Response Box */}
              <div className="p-3 rounded-lg bg-cyan-950/40 border border-cyan-800/60">
                <div className="text-cyan-400 font-semibold mb-1">Generated Conversational Response:</div>
                <p className="text-slate-200 italic">"{result.reply_message}"</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-xs">
              Submit an enquiry on the left to inspect real-time AI extraction and missing information analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
