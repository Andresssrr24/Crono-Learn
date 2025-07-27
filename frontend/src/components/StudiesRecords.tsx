import { useEffect, useState } from "react";
import { supabase } from "../services/supabase";

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

  useEffect(() => {
    async function fetchRecords() {
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
    }

    fetchRecords();
  }, []);

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
    "bg-emerald-900",
    "bg-teal-800",
    "bg-teal-900",
    "bg-teal-950"
  ];

  return (
    // Pinterest-stlye columns 
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
          </div>
        );
      })}
    </div>
)};