import { useEffect, useState } from "react";
import { supabase } from "../services/supabase";
import toast from "react-hot-toast";
import { EditRecordForm } from "./partials/EditRecordForm";

interface StudyRecord {
  id: number;
  topic?: string;
  study_time?: number;
  notes: string;
}

export function StudyRecords() {
  const [records, setRecords] = useState<StudyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [editingRecord, setEditingRecord] = useState<StudyRecord | null>(null);

  const fetchRecords = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      setIsLoggedIn(false);
      setLoading(false);
      return;
    }
    setIsLoggedIn(true);

    const { data, error } = await supabase
      .from("study_records")
      .select("*")
      .eq("user_id", user.id)
      .order("id", { ascending: false });

    if (error) {
      console.error("Error fetching records:", error.message);
    } else {
      setRecords(data || []);
    }

    setLoading(false);
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleDelete = async (id: number) => {
    const { error } = await supabase.from("study_records").delete().eq('id', id);
    if (error) {
      toast.error("Error deleting record");
    } else {
      toast.success("Record deleted");
      setRecords((prev) => prev.filter((rec) => rec.id !== id));
    }
  }

  if (loading) {
    return <p className="text-center text-gray-500 dark:text-gray-300">Loading study records...</p>;
  }

  if (!isLoggedIn) {
    return <p className="text-center text-red-500">You need to log in to see your records.</p>;
  }

  if (records.length === 0) {
    return <p className="text-center text-gray-600 dark:text-gray-400">No study records found yet.</p>;
  }

  // "Randomize" cards colors
  const colors = [
    "bg-green-700",
    "bg-green-800",
    "bg-green-900",
    "bg-emerald-700",
    "bg-emerald-600",
    "bg-green-900",
    "bg-teal-800",
    "bg-teal-900",
    "bg-green-600"
  ];

  return (
    <>
      <div className="ml-30 columns-2 sm:columns-3 lg:columns-5 gap-6 mt-4">
        {records.map((record) => {
          const randomColor = colors[Math.floor(Math.random() * colors.length)];
          return (
            <div
              key={record.id}
              className={`${randomColor} shadow-md border rounded-xl p-4 hover:shadow-xl transition duration-300 mb-6 break-inside-avoid`}
            >
              <h3 className="text-lg font-semibold text-gray-100">
                {record.topic || "Untitled Topic"}
              </h3>
              <p className="text-sm text-gray-300 mt-1">
                Study Time: {record.study_time ?? 0} min
              </p>
              <p className="text-sm text-gray-200 mt-2">Notes: {record.notes}</p>

              <div className="flex justify-end gap-2 mt-4">
                <button
                  onClick={() => setEditingRecord(record)}
                  className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(record.id)}
                  className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {editingRecord && (
        <EditRecordForm
          record={editingRecord}
          onClose={() => setEditingRecord(null)}
          onUpdated={fetchRecords}
        />
      )}
    </>
  );
}