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
  const contentType =
    response.headers.get("content-type") ?? "";

  let message = `Request failed with status ${response.status}`;

  if (contentType.includes("application/json")) {
    const errorBody = await response.json();

    if (typeof errorBody.detail === "string") {
      message = errorBody.detail;
    }
  } else {
    const text = await response.text();

    if (text) {
      message = `${message}: ${text.slice(0, 200)}`;
    }
  }

  throw new Error(message);
}

  return response.json();
}