import { useState } from "react";
import { supabase } from "../../services/supabase";
import toast from "react-hot-toast";

interface EditRecordProps {
    record: {
        id: number;
        topic?: string;
        study_time?: number;
        notes?: string;
    };
    onClose: () => void;
    onUpdated: () => void;
}

export function EditRecordForm({ record, onClose, onUpdated }: EditRecordProps) {
  const [topic, setTopic] = useState(record.topic || "");
  const [studyTime, setStudyTime] = useState<number | "">(record.study_time ?? "");
  const [notes, setNotes] = useState(record.notes || "");
  const [loading, setLoading] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studyTime || studyTime <= 0) {
        toast.error("Study time must be greater than 0.");
        return;
    }

    setLoading(true);

    const { error } = await supabase
        .from("study_records")
        .update({
            topic: topic.trim() || null,
            study_time: Number(studyTime),
            notes: notes.trim(),
        })
        .eq("id", record.id);

    setLoading(false);

    if (error) {
        toast.error("Error updating record.");
    } else {
        toast.success("Record updated");
        onUpdated();
        onClose();    
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-stone-900 rounded-xl shadow-lg p-6 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">
          Edit Record
        </h2>
        <form
          onSubmit={handleSave}
          className="flex flex-col gap-4 p-4 rounded-xl w-full max-w-md"
        >
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
            onChange={(e) =>
              setStudyTime(e.target.value === "" ? "" : Number(e.target.value))
            }
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

          <div className="flex justify-between">
            <button
              type="submit"
              disabled={loading}
              className="bg-teal-950 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg transition"
            >
              {loading ? "Saving..." : "Save Changes"}
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
      </div>
    </div>
  );
}

