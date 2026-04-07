import { useState, useEffect, type ChangeEvent, type FormEvent } from "react";
import "./App.css";
import { initDB } from "./db";
import { useStudy } from "./useStudy";

// Max file size: 100MB
const MAX_FILE_SIZE = 100 * 1024 * 1024;

function App() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const { processDocument, loading, error, result, isFromCache } = useStudy();

  useEffect(() => {
    initDB().catch((error) => {
      console.error("Failed to initialize database:", error);
    });
  }, []);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setFileError(null);
    
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        setFileError(`File size exceeds ${MAX_FILE_SIZE / (1024 * 1024)}MB limit. Please choose a smaller file.`);
        setPdfFile(null);
        return;
      }
    }
    setPdfFile(file);
  };

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!pdfFile) {
      return;
    }

    try {
      await processDocument(pdfFile);
      // Clear file after successful upload to free memory
      setPdfFile(null);
      setFileError(null);
      // Reset file input
      const fileInput = event.currentTarget.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err) {
      console.error("Failed to process document:", err);
    }
  };

  return (
    <main className="container upload-container">
      <div className="card">
        <h1>Upload a PDF or PPT</h1>
        <p>Choose a PDF or PowerPoint file and click the upload button. Supported formats: PDF (.pdf), PowerPoint 2007+ (.pptx), and PowerPoint 97-2003 (.ppt).</p>

        <form className="upload-form" onSubmit={handleUpload}>
          <label htmlFor="file-input" className="file-label">
            <span>Slide file</span>
            <input
              id="file-input"
              type="file"
              accept=".pdf,.ppt,.pptx,application/pdf,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation"
              onChange={handleFileChange}
              className="file-input"
            />
          </label>

          <div className="file-info">
            {pdfFile ? (
              <span className="selected-file">{pdfFile.name}</span>
            ) : (
              <span className="placeholder">No PDF selected</span>
            )}
          </div>

          <button type="submit" disabled={!pdfFile || loading}>
            {loading ? "Uploading…" : "Upload PDF"}
          </button>
        </form>

        {loading && (
          <div className="status-banner loading-banner">
            <span className="loader" /> Uploading and generating AI response…
          </div>
        )}

        {(error || fileError) && (
          <div className="status-banner error-banner">{error || fileError}</div>
        )}

        {isFromCache && !loading && (
          <div className="status-banner cache-banner">
            ✓ Loaded from offline cache
          </div>
        )}
      </div>

      {result && (
        <section className="response-card">
          <div className="response-section">
            <h2>Summary</h2>
            <p>{result.summary || "No summary available."}</p>
          </div>

          <div className="response-section">
            <h2>MCQs</h2>
            {result.mcqs.length > 0 ? (
              <div className="response-list">
                {result.mcqs.map((item, index) => (
                  <div key={index} className="response-item">
                    <p className="response-question">
                      {index + 1}. {item.question}
                    </p>
                    <ul>
                      {item.options.map((option, optionIndex) => (
                        <li key={optionIndex}>{option}</li>
                      ))}
                    </ul>
                    {item.answer && (
                      <p className="response-answer">Answer: {item.answer}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">No MCQs returned.</p>
            )}
          </div>

          <div className="response-section">
            <h2>Theory Questions</h2>
            {result.theory.length > 0 ? (
              <ol className="response-list">
                {result.theory.map((question, index) => (
                  <li key={index}>{question}</li>
                ))}
              </ol>
            ) : (
              <p className="empty-state">No theory questions returned.</p>
            )}
          </div>

          <div className="response-section">
            <h2>Flashcards</h2>
            {result.flashcards.length > 0 ? (
              <div className="flashcard-grid">
                {result.flashcards.map((card, index) => (
                  <article key={index} className="flashcard">
                    <strong>{card.term}</strong>
                    <p>{card.definition}</p>
                  </article>
                ))}
              </div>
            ) : (
              <p className="empty-state">No flashcards returned.</p>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
