import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

export async function generateYantra(payload: any) {
  const { data } = await api.post("/api/v1/generate/", payload);
  return data;
}
