import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { Login } from "../user_auth/Login";
 
export function SideNav() {
    const [isOpen, setIsOpen] =  useState(false);

    useEffect(() => {
        const resize = () => {
            if (window.innerWidth >= 800) {
                setIsOpen(true);
            } else {
                setIsOpen(false);
            }
        };

        window.addEventListener("resize", resize);
        resize();

        return  () => window.removeEventListener("resize", resize);
    }, []);

    return (
        <nav className={`fixed top-0 left-0 h-full bg-teal-950 border rounded-xl text-white transition-transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}>
            <ul className="flex flex-col p-4 space-y-2">
                <li>
                    <Link to="/" className="block p-2 rounded-lg hover:bg-emerald-900">Home</Link>
                </li>
                <li>
                    <Link to="/pomodoro" className="block p-2 rounded-lg hover:bg-emerald-900">Pomodoro</Link>
                </li>
            </ul>
            <div className="absolute bottom-0 left-0 w-full p-4 rounded-lg hover:bg-emerald-900">
                <Link to="/sign-in">
                    Login
                </Link>
            </div>
        </nav>
    )
}