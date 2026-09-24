"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

type Refund = {
  id: string;
  requested_amount: string;
  reason: string;
  status: string;
  customer: { name: string; email: string };
  order: { order_number: string; total_amount?: string; is_final_sale?: boolean };
  order_item: { id: string; product_name: string; is_damaged?: boolean; is_incorrect?: boolean };
  decision?: { outcome: string; reason_code: string; reason: string; ai_result: Record<string, unknown> };
  audit_logs?: Array<{ event_type: string; message: string }>;
};

type FormState = {
  customer_email: string;
  order_number: string;
  order_item_id: string;
  requested_amount: string;
  reason: string;
};

const emptyForm: FormState = {
  customer_email: "",
  order_number: "",
  order_item_id: "",
  requested_amount: "120.00",
  reason: "The item arrived damaged.",
};

export default function Home() {
  const [requests, setRequests] = useState<Refund[]>([]);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [filter, setFilter] = useState("ALL");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [apiError, setApiError] = useState("");

  async function load() {
    try {
      const response = await fetch(`${API}/refunds/requests/`, { cache: "no-store" });
      if (!response.ok) throw new Error(`Backend returned ${response.status}`);
      const data: Refund[] = await response.json();
      setRequests(data);
      if (data.length && !form.order_item_id) {
        const first = data[0];
        setForm((current) => ({
          ...current,
          customer_email: first.customer.email,
          order_number: first.order.order_number,
          order_item_id: first.order_item.id,
        }));
      }
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
      const response = await fetch(`${API}/refunds/requests/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
      setMessage(`Decision: ${data.decision?.outcome}. ${data.decision?.reason}`);
      setRequests((current) => [data, ...current]);
    } catch (error) {
      setMessage(`Request failed: ${String(error)}`);
    } finally {
      setLoading(false);
    }
  }

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
            <label>Email<input required value={form.customer_email} onChange={(e) => setForm({ ...form, customer_email: e.target.value })} /></label>
            <div className="row">
              <label>Order number<input required value={form.order_number} onChange={(e) => setForm({ ...form, order_number: e.target.value })} /></label>
              <label>Order item UUID<input required value={form.order_item_id} onChange={(e) => setForm({ ...form, order_item_id: e.target.value })} /></label>
            </div>
            <div className="row">
              <label>Amount<input required type="number" min="0.01" step="0.01" value={form.requested_amount} onChange={(e) => setForm({ ...form, requested_amount: e.target.value })} /></label>
              <label>Expected policy limit<input value="$500 automatic approval" disabled /></label>
            </div>
            <label>Customer reason<textarea required maxLength={5000} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} /></label>
            <button disabled={loading}>{loading ? "Processing…" : "Process refund request"}</button>
          </form>
          {message && <div className="result"><strong>{message}</strong></div>}
          <p className="muted">Select a seeded request from the dashboard to load valid customer/order/item identifiers automatically.</p>
        </section>

        <section className="card">
          <div className="card-heading"><div><p className="eyebrow">SUPPORT DASHBOARD</p><h2>Recent requests</h2></div></div>
          <div className="filters">
            {["ALL", "APPROVED", "DENIED", "ESCALATED"].map((value) => <button key={value} className={filter === value ? "filter active" : "filter"} onClick={() => setFilter(value)}>{value}</button>)}
          </div>
          {visibleRequests.length === 0 ? <p className="muted">No requests match this filter.</p> : visibleRequests.slice(0, 15).map((request) => (
            <button className="request" key={request.id} onClick={() => selectRequest(request)}>
              <div className="request-top"><span className={`badge ${request.status.toLowerCase()}`}>{request.status}</span><strong>{request.order.order_number}</strong><span>${request.requested_amount}</span></div>
              <div>{request.customer.name} · {request.order_item.product_name}</div>
              <div className="muted">{request.decision?.reason_code}: {request.decision?.reason}</div>
              {request.decision?.ai_result && Object.keys(request.decision.ai_result).length > 0 && <div className="ai-note">AI analysis available · {String(request.decision.ai_result.classification || "classified")}</div>}
            </button>
          ))}
        </section>
      </div>

      <footer>Hard policy rules remain authoritative. AI output is validated and cannot override DENIED or ESCALATED policy outcomes.</footer>
    </main>
  );
}
