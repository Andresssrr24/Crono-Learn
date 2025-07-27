import { StudyRecords } from "../components/StudiesRecords"
import { useEffect, useState } from "react";
import { supabase } from "../services/supabase";
import { Dialog, DialogPanel, DialogTitle } from "@headlessui/react";
import { AddRecordForm } from "../components/partials/AddRecordForm";

export function StudiesPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);

  useEffect(() => {
    async function checkAuth() {
      const { data: { user } } = await supabase.auth.getUser();
      setIsLoggedIn(!!user);
    }
    checkAuth();
  }, []);

  const handleAddRecord = () => {
    if (isLoggedIn) {
      setIsFormOpen(true);  
    } else {
      window.location.href = "/sign-in";
    }
  };

  return (
    <div className="min-h-screen px-4 py-10 flex flex-col gap-4">
      <h1 className="text-4xl font-bold text-gray-100 self-center">My Studies</h1>
      <button 
        onClick={handleAddRecord}
        className="bg-teal-950 text-white px-5 py-2 rounded-xl hover:bg-emerald-700 transition self-center"
      >
        Add Record
      </button>
      <div className="w-full">
        <StudyRecords />  
      </div>  

      <Dialog open={isFormOpen} onClose={() => setIsFormOpen(false)} className="relaitve z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
            <DialogPanel className="bg-stone-900 p-6 rounded-xl shadow-xl max-w-md w-full">
                <DialogTitle className="text-xl font-bold mb-2 text-gray-800 dark:text-gray-100">
                    Add a new study record
                </DialogTitle>
                <AddRecordForm onClose={() => setIsFormOpen(false)} />
            </DialogPanel>
        </div>
      </Dialog>
    </div>
  );
}
