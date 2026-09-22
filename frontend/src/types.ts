export interface DashboardMetrics {
  total_leads: number;
  new_leads: number;
  qualified_leads: number;
  quoted_leads: number;
  booked_leads: number;
  total_quotes: number;
  pending_quotes: number;
  approved_quotes: number;
  pending_followups: number;
  failed_tasks: number;
  conversion_rate_pct: number;
  emergency_stop_active: boolean;
}

export interface RevenueMetrics {
  mrr: number;
  arr: number;
  gross_booking_revenue: number;
  operating_expenses: number;
  gross_margin: number;
  gross_margin_pct: number;
  customer_count: number;
  currency: string;
}

export interface LeadItem {
  id: string;
  business_id: string;
  customer_id: string;
  customer_name: string;
  customer_phone?: string;
  destination?: string;
  origin?: string;
  travel_date?: string;
  passenger_count?: number;
  vehicle_type?: string;
  budget?: number;
  status: string;
  lead_score: number;
  created_at: string;
}

export interface ExtractedRequirement {
  origin?: string;
  destination?: string;
  vehicle_type?: string;
  duration_days?: number;
  travel_date?: string;
  passenger_count?: number;
  budget?: number;
  confidence: number;
}

export interface EnquiryResponse {
  lead_id: string;
  customer_id: string;
  extracted: ExtractedRequirement;
  missing_fields: string[];
  reply_message: string;
  lead_score: number;
}

export interface DailyReport {
  date: string;
  enquiries_count: number;
  qualified_leads: number;
  quotes_generated: number;
  quotes_accepted: number;
  bookings_count: number;
  revenue_amount: number;
  pending_followups: number;
  failed_tasks: number;
  estimated_ai_cost: number;
  net_contribution: number;
}

export interface Quotation {
  id: string;
  lead_id: string;
  quotation_number: string;
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  currency: string;
  status: string;
  created_at: string;
}
