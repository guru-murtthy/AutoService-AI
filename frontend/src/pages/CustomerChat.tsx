import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Send, Bot, User, FileText, CheckCircle2, Car, MapPin } from 'lucide-react';

export const CustomerChatView: React.FC = () => {
  const { businessId } = useParams<{ businessId: string }>();
  const [customerName, setCustomerName] = useState('');
  const [phone, setPhone] = useState('');
  const [message, setMessage] = useState('');
  const [isRegistered, setIsRegistered] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [lead, setLead] = useState<any>(null);
  const [quotation, setQuotation] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isRegistered && phone) {
      loadHistory();
      const interval = setInterval(loadHistory, 4000);
      return () => clearInterval(interval);
    }
  }, [isRegistered, phone, businessId]);

  const loadHistory = async () => {
    try {
      const res = await axios.get(`/api/v1/public/chat/${businessId || 'demo_business_id'}/history`, {
        params: { phone }
      });
      setMessages(res.data.messages || []);
      setLead(res.data.lead);
      setQuotation(res.data.quotation);
    } catch (e) {
      console.error(e);
    }
  };

  const handleStartChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName || !phone) return;
    setIsRegistered(true);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userText = message;
    setMessage('');
    setLoading(true);

    try {
      await axios.post(`/api/v1/public/chat/${businessId || 'demo_business_id'}/message`, {
        customer_name: customerName,
        phone,
        message: userText
      });
      loadHistory();
    } catch (e) {
      alert("Error sending message");
    } finally {
      setLoading(false);
    }
  };

  if (!isRegistered) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="glass-card p-8 rounded-2xl max-w-md w-full space-y-6 border border-slate-800">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 rounded-2xl gradient-btn flex items-center justify-center mx-auto text-white shadow-lg shadow-cyan-500/20">
              <Car className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-bold text-white">Instant Travel Enquiry Portal</h1>
            <p className="text-xs text-slate-400">Connect directly with our AI travel assistant for instant quotations</p>
          </div>

          <form onSubmit={handleStartChat} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Your Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Rahul Sharma"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">WhatsApp / Phone Number</label>
              <input
                type="text"
                required
                placeholder="e.g. +91 98765 43210"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl gradient-btn text-white font-semibold text-sm shadow-lg"
            >
              Start Live Chat
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col max-w-3xl mx-auto border-x border-slate-800/60 shadow-2xl">
      {/* Top Header */}
      <header className="p-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between sticky top-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full gradient-btn flex items-center justify-center text-white">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">AI Travel Concierge</div>
            <div className="text-[11px] text-emerald-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Online • Instant Quoting
            </div>
          </div>
        </div>

        {quotation && (
          <a
            href={quotation.pdf_url}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold flex items-center gap-1.5 hover:bg-emerald-500/30 transition"
          >
            <FileText className="w-4 h-4" /> Download PDF Quote (₹{quotation.total?.toLocaleString()})
          </a>
        )}
      </header>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        <div className="text-center my-2">
          <span className="px-3 py-1 rounded-full bg-slate-900 text-slate-400 text-[10px] border border-slate-800 font-mono">
            Chatting as {customerName} ({phone})
          </span>
        </div>

        {messages.map((m) => {
          const isAi = m.sender === 'ai';
          return (
            <div key={m.id} className={`flex gap-3 ${isAi ? 'justify-start' : 'justify-end'}`}>
              {isAi && (
                <div className="w-7 h-7 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center shrink-0 text-xs">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div className={`p-3.5 rounded-2xl max-w-[80%] text-xs leading-relaxed ${
                isAi
                  ? 'bg-slate-900 text-slate-100 border border-slate-800 rounded-tl-none'
                  : 'bg-cyan-600 text-white rounded-tr-none font-medium'
              }`}>
                {m.message}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex gap-2 text-slate-400 text-xs items-center pl-2">
            <Bot className="w-4 h-4 text-cyan-400 animate-spin" /> AI Assistant thinking...
          </div>
        )}
      </div>

      {/* Input Footer */}
      <form onSubmit={handleSendMessage} className="p-3 bg-slate-900/90 border-t border-slate-800 flex gap-2">
        <input
          type="text"
          placeholder="e.g. Need a 7 seater from Bangalore to Coorg for 3 days starting Oct 10"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-2.5 rounded-xl gradient-btn text-white font-semibold text-xs flex items-center gap-1.5 shadow-md"
        >
          <Send className="w-4 h-4" /> Send
        </button>
      </form>
    </div>
  );
};
