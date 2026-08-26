import type { QueryResponse } from "./types";

const API_URL =
  import.meta.env.VITE_API_URL ??
  "/api";

export async function askSqlAgent(
  question: string
): Promise<QueryResponse> {
  const response = await fetch(
    `${API_URL}/ai/query`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        question,
      }),
    }
  );

  if (!response.ok) {
    const errorBody = await response.json();

    const message =
      typeof errorBody.detail === "string"
        ? errorBody.detail
        : JSON.stringify(errorBody.detail);

    throw new Error(
      message || "Request failed"
    );
  }

  return response.json();
}