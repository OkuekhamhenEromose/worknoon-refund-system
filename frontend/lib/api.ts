const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export type RefundRequestPayload = {
  customer_email: string;
  order_number: string;
  order_item_id: string;
  requested_amount: string;
  reason: string;
};

export async function getRefundRequests(): Promise<Response> {
  return fetch(`${API_BASE_URL}/refunds/requests/`, { cache: "no-store" });
}

export async function createRefundRequest(payload: RefundRequestPayload): Promise<Response> {
  return fetch(`${API_BASE_URL}/refunds/requests/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
