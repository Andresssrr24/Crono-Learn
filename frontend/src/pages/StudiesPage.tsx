import { StudyRecords } from "../components/StudiesRecords"
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { supabase } from "../services/supabase";

export function StudiesPage() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    async function checkAuth() {
      const { data: { user } } = await supabase.auth.getUser();
      setIsLoggedIn(!!user);
    }
    checkAuth();
  }, []);

  const handleAddRecord = () => {
    if (isLoggedIn) {
      navigate("/add-record");  // o la ruta para crear un nuevo registro
    } else {
      navigate("/sign-in");
    }
  };

  return (
    <div className="min-h-screen px-4 py-10 flex flex-col items-center gap-6 bg-gray-100 dark:bg-gray-900">
      <h1 className="text-4xl font-bold text-center text-gray-800 dark:text-gray-100">My Studies</h1>
      <button 
        onClick={handleAddRecord}
        className="bg-indigo-600 text-white px-5 py-2 rounded-xl hover:bg-indigo-700 transition"
      >
        Add Record
      </button>
      <StudyRecords />
    </div>
  );
}
