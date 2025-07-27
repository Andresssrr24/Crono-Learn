import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { supabase } from "../../services/supabase";
import { type Session } from "@supabase/supabase-js";
import { useNavigate } from "react-router-dom";
 
export function SideNav() {
    const navigate = useNavigate();
    const [isOpen, setIsOpen] =  useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);    
    const [session, setSession] = useState<Session | null>(null);

    useEffect(() => {
        const resize = () => {
            setIsOpen(window.innerWidth >= 800);
        };

        resize();
        window.addEventListener("resize", resize);
        return () => window.removeEventListener("resize", resize);
    }, []);

    useEffect(() => {
        const fetchSession = async () => {
        const { data } = await supabase.auth.getSession();
        setSession(data.session);
        };

        fetchSession();

        const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
        setSession(newSession);
        });

        return () => {
        listener.subscription.unsubscribe();
        };
    }, []);

    const handleLogout = async () => {
        await supabase.auth.signOut();
        setIsDropdownOpen(false);
        navigate('/')
    };

    return (
        <nav className={`fixed top-4 left-4  h-[90vh] bg-teal-950 border border-emerald-700 rounded-xl text-white transition-transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}>
            <div className="flex flex-col h-full">
                <ul className="flex flex-col space-y-2">
                    <li>
                        <Link to="/" className="block p-2 rounded-lg hover:bg-emerald-900">Home</Link>
                    </li>
                    <li>
                        <Link to="/pomodoro" className="block p-2 rounded-lg hover:bg-emerald-900">Pomodoro</Link>
                    </li>
                    <li>
                        <Link to="/my-studies" className="block p-2 rounded-lg hover:bg-emerald-900">My studies</Link>
                    </li>
                </ul>

                <ul className="p-4 mt-auto">
                    <li
                        className="relative group"
                        onMouseEnter={() => setIsDropdownOpen(true)}
                        onMouseLeave={() => setIsDropdownOpen(false)}
                    >
                        <div className="block p-2 rounded-lg hover:bg-emerald-900 cursor-pointer">
                            👤 User
                        </div>
                        <ul className={`absolute left-full bottom-0 mb-2 ml-2 w-40 bg-teal-900 rounded-lg shadow-lg transition-opacity duration-200 ${isDropdownOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
                            <li>
                                <Link to="/settings" className="block px-4 py-2 hover:bg-emerald-800 rounded-t-lg">Settings</Link>
                            </li>
                            <li>
                                <Link to="/profile" className="block px-4 py-2 hover:bg-emerald-800">Profile</Link>
                            </li>

                            {!session ? (
                                <>
                                    <li>
                                        <Link to="/sign-up" className="block px-4 py-2 hover:bg-emerald-800">Sign Up</Link>
                                    </li>
                                    <li>
                                        <Link to="/sign-in" className="block px-4 py-2 hover:bg-emerald-800 rounded-b-lg">Log In</Link>
                                    </li>
                                </>
                            ) : (
                                <li>
                                    <button
                                        onClick={handleLogout}
                                        className="w-full text-left px-4 py-2 hover:bg-emerald-800 rounded-b-lg"
                                    >
                                        Log Out
                                    </button>
                                </li>
                            )}
                        </ul>
                    </li>
                </ul>
            </div>    
        </nav>
    )
}