import { useState } from "react";
import api from "./api";

type Experience =
  | "Excellent"
  | "Good"
  | "Average"
  | "Poor";

type Usefulness =
  | "Yes"
  | "Somewhat"
  | "No";

export default function Feedback() {
  const [experience, setExperience] =
    useState<Experience | "">("");

  const [usefulness, setUsefulness] =
    useState<Usefulness | "">("");

  const [improvement, setImprovement] =
    useState<string>("");

  const [message, setMessage] =
    useState<string>("");

  const [error, setError] =
    useState<string>("");

  const [loading, setLoading] =
    useState<boolean>(false);

  const submitFeedback = async () => {
    setMessage("");
    setError("");

    if (!experience) {
      setError(
        "Please select your experience."
      );
      return;
    }

    if (!usefulness) {
      setError(
        "Please tell us whether the quiz was useful."
      );
      return;
    }

    try {
      setLoading(true);

      const response = await api.post(
        "/api/feedback",
        {
          experience,
          usefulness,
          improvement,
        }
      );

      setMessage(
        response.data?.message ||
          "Thank you for your feedback!"
      );

      setExperience("");
      setUsefulness("");
      setImprovement("");

    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
          "Failed to submit feedback."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="config-card"
      style={{ marginTop: "24px" }}
    >
      <div className="source-pill">
        💬 Your Feedback
      </div>

      <h2>
        How was your experience?
      </h2>

      <p className="muted">
        Your feedback helps us improve QuizMate AI.
      </p>

      {/* EXPERIENCE */}

      <label>
        How was your experience?
      </label>

      <div className="options">
        {(
          [
            "Excellent",
            "Good",
            "Average",
            "Poor",
          ] as Experience[]
        ).map((option) => (
          <button
            key={option}
            type="button"
            className={
              experience === option
                ? "option selected"
                : "option"
            }
            onClick={() =>
              setExperience(option)
            }
          >
            {option}
          </button>
        ))}
      </div>

      {/* USEFULNESS */}

      <label
        style={{
          display: "block",
          marginTop: "20px",
        }}
      >
        Was the quiz useful?
      </label>

      <div className="options">
        {(
          [
            "Yes",
            "Somewhat",
            "No",
          ] as Usefulness[]
        ).map((option) => (
          <button
            key={option}
            type="button"
            className={
              usefulness === option
                ? "option selected"
                : "option"
            }
            onClick={() =>
              setUsefulness(option)
            }
          >
            {option}
          </button>
        ))}
      </div>

      {/* IMPROVEMENT */}

      <label
        style={{
          display: "block",
          marginTop: "20px",
        }}
      >
        What can we improve?
      </label>

      <textarea
        className="answer-box"
        value={improvement}
        onChange={(
          e: React.ChangeEvent<HTMLTextAreaElement>
        ) =>
          setImprovement(e.target.value)
        }
        placeholder="Tell us what you think..."
        rows={4}
      />

      {/* ERROR */}

      {error && (
        <div
          className="error"
          style={{ marginTop: "12px" }}
        >
          {error}
        </div>
      )}

      {/* SUCCESS */}

      {message && (
        <div
          className="success"
          style={{ marginTop: "12px" }}
        >
          {message}
        </div>
      )}

      {/* SUBMIT */}

      <button
        className="primary big"
        type="button"
        disabled={
          loading ||
          !experience ||
          !usefulness
        }
        onClick={submitFeedback}
        style={{ marginTop: "16px" }}
      >
        {loading
          ? "Submitting..."
          : "Submit Feedback"}
      </button>
    </div>
  );
}