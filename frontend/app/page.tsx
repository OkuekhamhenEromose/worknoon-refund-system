"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { createRefundRequest, getRefundRequests, RefundRequestPayload } from "../lib/api";

type Refund = {
  id: string;
  requested_amount: string;
  reason: string;
  status: string;
  created_at: string;
  customer: { name: string; email: string };
  order: { order_number: string; total_amount?: string; currency?: string; status?: string; is_final_sale?: boolean };
  order_item: { id: string; product_name: string; sku?: string; is_damaged?: boolean; is_incorrect?: boolean };
  decision?: {
    outcome: string;
    reason_code: string;
    reason: string;
    policy_result?: Record<string, unknown>;
    ai_result: Record<string, unknown>;
  };
  audit_logs?: Array<{ event_type: string; message: string; created_at?: string }>;
};

const emptyForm: RefundRequestPayload = {
  customer_email: "",
  order_number: "",
  order_item_id: "",
  requested_amount: "120.00",
  reason: "The item arrived damaged.",
};

export default function Home() {
  const [requests, setRequests] = useState<Refund[]>([]);
  const [form, setForm] = useState<RefundRequestPayload>(emptyForm);
  const [selected, setSelected] = useState<Refund | null>(null);
  const [filter, setFilter] = useState("ALL");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [apiError, setApiError] = useState("");

  async function load() {
    try {
      const response = await getRefundRequests();
      if (!response.ok) throw new Error(`Backend returned ${response.status}`);
      const data: Refund[] = await response.json();
      setRequests(data);
      setSelected((current) => current ? data.find((item) => item.id === current.id) || current : null);
      if (data.length && !form.order_item_id) selectRequest(data[0]);
      setApiError("");
    } catch (error) {
      setApiError(`Backend unavailable: ${String(error)}`);
    }
  }

  useEffect(() => { load(); }, []);

  const visibleRequests = useMemo(
    () => filter === "ALL" ? requests : requests.filter((request) => request.status === filter),
    [filter, requests],
  );

  const counts = useMemo(() => ({
    total: requests.length,
    approved: requests.filter((r) => r.status === "APPROVED").length,
    denied: requests.filter((r) => r.status === "DENIED").length,
    escalated: requests.filter((r) => r.status === "ESCALATED").length,
  }), [requests]);

  function selectRequest(request: Refund) {
    setSelected(request);
    setForm({
      customer_email: request.customer.email,
      order_number: request.order.order_number,
      order_item_id: request.order_item.id,
      requested_amount: request.requested_amount,
      reason: request.reason,
    });
    setMessage(`Loaded ${request.order.order_number} / ${request.order_item.product_name}`);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const response = await createRefundRequest(form);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
      setMessage(`Decision: ${data.decision?.outcome}. ${data.decision?.reason}`);
      setSelected(data);
      setRequests((current) => [data, ...current.filter((item) => item.id !== data.id)]);
    } catch (error) {
      setMessage(`Request failed: ${String(error)}`);
    } finally {
      setLoading(false);
    }
  }

  const ai = selected?.decision?.ai_result || {};
  const auditLogs = selected?.audit_logs || [];

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">WORKNOON AI ASSESSMENT</p>
          <h1>Refund Support Console</h1>
          <p className="muted">AI-assisted support workflow with deterministic policy enforcement and an auditable decision trail.</p>
        </div>
        <button className="secondary" onClick={load}>Refresh</button>
      </header>

      {apiError && <div className="alert">{apiError}</div>}

      <section className="stats">
        <div className="stat"><span>Total</span><strong>{counts.total}</strong></div>
        <div className="stat"><span>Approved</span><strong>{counts.approved}</strong></div>
        <div className="stat"><span>Denied</span><strong>{counts.denied}</strong></div>
        <div className="stat"><span>Escalated</span><strong>{counts.escalated}</strong></div>
      </section>

      <div className="grid">
        <section className="card">
          <div className="card-heading"><div><p className="eyebrow">CUSTOMER FLOW</p><h2>Submit refund request</h2></div></div>
          <form onSubmit={submit}>
            <label>Email<input required type="email" value={form.customer_email} onChange={(e) => setForm({ ...form, customer_email: e.target.value })} /></label>
            <div className="row">
              <label>Order number<input required value={form.order_number} onChange={(e) => setForm({ ...form, order_number: e.target.value })} /></label>
              <label>Order item UUID<input required value={form.order_item_id} onChange={(e) => setForm({ ...form, order_item_id: e.target.value })} /></label>
            </div>
            <div className="row">
              <label>Amount<input required type="number" min="0.01" step="0.01" value={form.requested_amount} onChange={(e) => setForm({ ...form, requested_amount: e.target.value })} /></label>
              <label>Automatic approval limit<input value="$500" disabled /></label>
            </div>
            <label>Customer reason<textarea required maxLength={5000} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} /></label>
            <button disabled={loading}>{loading ? "Processing…" : "Process refund request"}</button>
          </form>
          {message && <div className="result"><strong>{message}</strong></div>}
          <p className="muted">Select a seeded request from the dashboard to load valid customer, order, and item identifiers automatically.</p>
        </section>

        <section className="card">
          <div className="card-heading"><div><p className="eyebrow">SUPPORT DASHBOARD</p><h2>Recent requests</h2></div></div>
          <div className="filters">
            {["ALL", "APPROVED", "DENIED", "ESCALATED"].map((value) => (
              <button key={value} className={filter === value ? "filter active" : "filter"} onClick={() => setFilter(value)}>{value}</button>
            ))}
          </div>
          {visibleRequests.length === 0 ? <p className="muted">No requests match this filter.</p> : visibleRequests.slice(0, 15).map((request) => (
            <button className={`request ${selected?.id === request.id ? "selected" : ""}`} key={request.id} onClick={() => selectRequest(request)}>
              <div className="request-top"><span className={`badge ${request.status.toLowerCase()}`}>{request.status}</span><strong>{request.order.order_number}</strong><span>${request.requested_amount}</span></div>
              <div>{request.customer.name} · {request.order_item.product_name}</div>
              <div className="muted">{request.decision?.reason_code || "PENDING"}: {request.decision?.reason || "Awaiting processing"}</div>
            </button>
          ))}
        </section>
      </div>

      <section className="detail-grid">
        <section className="card">
          <p className="eyebrow">DECISION DETAIL</p>
          <h2>{selected ? selected.order.order_number : "Select a request"}</h2>
          {selected ? (
            <>
              <div className="detail-row"><span>Outcome</span><strong className={`badge ${selected.status.toLowerCase()}`}>{selected.status}</strong></div>
              <div className="detail-row"><span>Policy reason</span><strong>{selected.decision?.reason_code || "PENDING"}</strong></div>
              <p>{selected.decision?.reason || "This seeded request has not been processed yet."}</p>
              {typeof ai.customer_response === "string" && <div className="customer-response"><p className="eyebrow">AI CUSTOMER RESPONSE</p><p>{ai.customer_response}</p></div>}
              {typeof ai.reasoning_summary === "string" && <p className="muted"><strong>AI reasoning:</strong> {ai.reasoning_summary}</p>}
              {Array.isArray(ai.risk_flags) && ai.risk_flags.length > 0 && <p className="risk"><strong>Risk flags:</strong> {ai.risk_flags.join(", ")}</p>}
            </>
          ) : <p className="muted">Use the request list to inspect policy, AI, and audit information.</p>}
        </section>

        <section className="card">
          <p className="eyebrow">AUDIT TRAIL</p>
          <h2>Workflow events</h2>
          {auditLogs.length === 0 ? <p className="muted">No audit events available for this request.</p> : auditLogs.map((log, index) => (
            <div className="audit" key={`${log.event_type}-${index}`}><strong>{log.event_type}</strong><span>{log.message}</span></div>
          ))}
        </section>
      </section>

      <footer>Hard policy rules remain authoritative. AI output is validated, risk signals are auditable, and AI cannot override hard policy decisions.</footer>
    </main>
  );
}
