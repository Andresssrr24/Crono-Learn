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

  return (
    <div className="w-full max-w-5xl grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
      {records.map((record) => (
        <div
          key={record.id}
          className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-4 hover:shadow-xl transition duration-300"
        >
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
            {record.topic || "Untitled Topic"}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
            Study Time: {record.study_time ?? 0} min
          </p>
          <p className="text-sm text-gray-700 dark:text-gray-200 mt-2">
            Notes: {record.notes}
          </p>
        </div>
      ))}
    </div>
  );
}
