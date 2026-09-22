import axios from 'axios';
import { DashboardMetrics, RevenueMetrics, LeadItem, EnquiryResponse, DailyReport, Quotation } from '../types';

const API_BASE = '/api/v1';

export const api = {
  getDashboardSummary: async (businessId: string): Promise<{ metrics: DashboardMetrics; revenue: RevenueMetrics }> => {
    const res = await axios.get(`${API_BASE}/dashboard/summary`, { params: { business_id: businessId } });
    return res.data;
  },

  getLeads: async (businessId: string): Promise<LeadItem[]> => {
    const res = await axios.get(`${API_BASE}/leads`, { params: { business_id: businessId } });
    return res.data;
  },

  updateLeadStatus: async (leadId: string, status: string): Promise<LeadItem> => {
    const res = await axios.patch(`${API_BASE}/leads/${leadId}/status`, { status });
    return res.data;
  },

  submitEnquiry: async (businessId: string, customerName: string, message: string, phone?: string): Promise<EnquiryResponse> => {
    const res = await axios.post(`${API_BASE}/enquiries`, {
      business_id: businessId,
      customer_name: customerName,
      message,
      phone
    });
    return res.data;
  },

  calculateQuote: async (businessId: string, vehicleType: string, durationDays: number, estimatedKm?: number) => {
    const res = await axios.post(`${API_BASE}/quotations/calculate`, {
      business_id: businessId,
      vehicle_type: vehicleType,
      duration_days: durationDays,
      estimated_km: estimatedKm
    });
    return res.data;
  },

  getDailyReport: async (businessId: string): Promise<DailyReport> => {
    const res = await axios.get(`${API_BASE}/reports/daily`, { params: { business_id: businessId } });
    return res.data;
  },

  triggerEmergencyStop: async (reason: string) => {
    const res = await axios.post(`${API_BASE}/admin/emergency-stop`, { reason });
    return res.data;
  },

  resumeNormalOperations: async () => {
    const res = await axios.post(`${API_BASE}/admin/emergency-stop/deactivate`);
    return res.data;
  },

  getEmergencyStatus: async () => {
    const res = await axios.get(`${API_BASE}/admin/emergency-stop/status`);
    return res.data;
  }
};
