import { useState } from "react";

function App() {

  const [url, setUrl] =
    useState("");

  const [result, setResult] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const crawl = async () => {

    if (!url) return;

    setLoading(true);

    try {

      const response =
        await fetch(
          "http://localhost:5000/chat",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json"
            },
            body: JSON.stringify({
              message: `Crawl ${url}`
            })
          }
        );

      const data =
        await response.json();

      setResult(
        data.answer
      );

    } catch {

      setResult(
        "Error calling backend"
      );

    }

    setLoading(false);
  };

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "40px auto",
        padding: "20px"
      }}
    >

      <h1>
        Web Crawler Agent
      </h1>

      <input
        type="text"
        value={url}
        onChange={(e) =>
          setUrl(e.target.value)
        }
        placeholder="https://example.com"
        style={{
          width: "100%",
          padding: "10px"
        }}
      />

      <br />
      <br />

      <button
        onClick={crawl}
      >
        Crawl
      </button>

      <br />
      <br />

      {
        loading &&
        <p>Loading...</p>
      }

      <pre
        style={{
          whiteSpace: "pre-wrap"
        }}
      >
        {result}
      </pre>

    </div>
  );
}

export default App;