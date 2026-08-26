import { useState } from "react";
import type { FormEvent } from "react";

import { askSqlAgent } from "./api";
import type { QueryResponse } from "./types";

import "./App.css";


function App() {
  const [question, setQuestion] = useState(
    "What are the top 5 products by revenue?"
  );

  const [result, setResult] =
    useState<QueryResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const trimmedQuestion =
      question.trim();

    if (!trimmedQuestion) {
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await askSqlAgent(
        trimmedQuestion
      );

      setResult(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "An unexpected error occurred."
        );
      }
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="page">
      <section className="container">

        <header className="hero">
          <p className="eyebrow">
            Azure OpenAI · FastAPI · PostgreSQL
          </p>

          <h1>AI SQL Agent</h1>

          <p className="subtitle">
            Ask questions about the sales
            database using natural language.
          </p>
        </header>


        <section className="card query-card">

          <form onSubmit={handleSubmit}>

            <label htmlFor="question">
              Ask a question
            </label>

            <textarea
              id="question"
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }
              rows={4}
              placeholder="Example: Which customers generated the most revenue?"
            />

            <button
              type="submit"
              disabled={
                loading ||
                !question.trim()
              }
            >
              {loading
                ? "Running query..."
                : "Ask SQL Agent"}
            </button>

          </form>

        </section>


        {error && (
          <section className="card error-card">
            <h2>Request failed</h2>
            <p>{error}</p>
          </section>
        )}


        {result && (
          <>

            <section className="card">
              <div className="section-header">
                <h2>AI Answer</h2>

                <span className="badge">
                  {result.attempt_count}
                  {" "}
                  attempt
                  {result.attempt_count !== 1
                    ? "s"
                    : ""}
                </span>
              </div>

              <p className="answer">
                {result.answer}
              </p>
            </section>


            <section className="card">
              <h2>Generated SQL</h2>

              <p className="purpose">
                {result.purpose}
              </p>

              <pre className="sql-block">
                <code>
                  {result.sql}
                </code>
              </pre>
            </section>


            <section className="card">
              <div className="section-header">

                <h2>Query Results</h2>

                <span className="badge">
                  {result.row_count} rows
                </span>

              </div>


              {result.rows.length === 0 ? (

                <p>No rows returned.</p>

              ) : (

                <div className="table-wrapper">

                  <table>

                    <thead>
                      <tr>

                        {result.columns.map(
                          (column) => (
                            <th key={column}>
                              {column}
                            </th>
                          )
                        )}

                      </tr>
                    </thead>


                    <tbody>

                      {result.rows.map(
                        (row, rowIndex) => (

                          <tr key={rowIndex}>

                            {result.columns.map(
                              (column) => (

                                <td
                                  key={
                                    `${rowIndex}-${column}`
                                  }
                                >
                                  {formatCell(
                                    row[column]
                                  )}
                                </td>

                              )
                            )}

                          </tr>

                        )
                      )}

                    </tbody>

                  </table>

                </div>

              )}

            </section>

          </>
        )}

      </section>
    </main>
  );
}


function formatCell(
  value: unknown
): string {
  if (value === null) {
    return "NULL";
  }

  if (
    typeof value === "object"
  ) {
    return JSON.stringify(value);
  }

  return String(value);
}


export default App;