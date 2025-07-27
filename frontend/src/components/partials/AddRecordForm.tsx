import { useState } from "react";
import { createStudyRecord } from "../../services/api/study_records";

export function AddRecordForm({ onClose }: { onClose: () => void }) {
  const [topic, setTopic] = useState("");
  const [studyTime, setStudyTime] = useState<number | "">("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!studyTime || studyTime <= 0) {
      setError("Study time is required and must be greater than 0.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await createStudyRecord({
        topic: topic.trim() || null,
        study_time: Number(studyTime),
        notes: notes.trim() || null,
      });
      onClose();
    } catch (err) {
      console.error(err);
      setError("Error saving record. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-4 rounded-xl w-full max-w-md">
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Topic (optional)"
        className="border border-neutral-600 rounded-md p-2 focus:outline-none focus:ring focus:ring-teal-400"
      />

      <input
        type="number"
        value={studyTime}
        required
        onChange={(e) => setStudyTime(e.target.value === "" ? "" : Number(e.target.value))}
        placeholder="Study Time (in minutes)"
        className="border border-neutral-600 rounded-md p-2 focus:outline-none focus:ring focus:ring-teal-400"
      />

      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Notes (optional)"
        rows={4}
        className="border border-neutral-600 rounded-md p-2 resize-none focus:outline-none focus:ring focus:ring-teal-400"
      />

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <div className="flex justify-between">
        <button
          type="submit"
          disabled={loading}
          className="bg-teal-950 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg transition"
        >
          {loading ? "Saving..." : "Save Record"}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="text-gray-500 hover:underline"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

