export type QueryRow = Record<string, unknown>;

export interface QueryResponse {
  question: string;
  status: string;
  sql: string;
  purpose: string;
  answer: string;
  columns: string[];
  rows: QueryRow[];
  row_count: number;
  attempt_count: number;
}