// const API_BASE_URL =
//   process.env.NEXT_PUBLIC_API_BASE_URL ||
//   "http://localhost:8000/api/v1";

// export async function getRefundRequests() {
//   const response = await fetch(
//     `${API_BASE_URL}/refunds/requests/`
//   );

//   if (!response.ok) {
//     throw new Error("Failed to load refund requests");
//   }

//   return response.json();
// }

// export async function createRefundRequest(data: {
//   customer_email: string;
//   order_number: string;
//   order_item_id: string;
//   requested_amount: string;
//   reason: string;
// }) {
//   const response = await fetch(
//     `${API_BASE_URL}/refunds/requests/`,
//     {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify(data),
//     }
//   );

//   const result = await response.json();

//   if (!response.ok) {
//     throw new Error(
//       result.detail || JSON.stringify(result)
//     );
//   }

//   return result;
// }
