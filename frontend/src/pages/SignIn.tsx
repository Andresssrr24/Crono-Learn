import { Login } from "../components/user_auth/Login";
import { Link } from "react-router-dom";

export function SignInPage() {
    return (
        <div>
            <Link to={'/'}>CRONOLEARN</Link>
            <Login />
        </div>
    );
}